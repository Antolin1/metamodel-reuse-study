package emfcompare;

import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.io.PrintWriter;
import java.io.Reader;
import java.util.Comparator;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Map.Entry;
import java.util.stream.Collectors;

import org.apache.commons.csv.CSVFormat;
import org.apache.commons.csv.CSVParser;
import org.apache.commons.csv.CSVRecord;
import org.eclipse.emf.compare.AttributeChange;
import org.eclipse.emf.compare.Diff;
import org.eclipse.emf.compare.DifferenceKind;
import org.eclipse.emf.compare.Match;
import org.eclipse.emf.compare.ReferenceChange;
import org.eclipse.emf.compare.ResourceAttachmentChange;
import org.eclipse.emf.ecore.EClass;
import org.eclipse.emf.ecore.EcorePackage;

/**
 * Auxiliary script used to analyse different meta-model samples during the work
 */
public class ClusterFineGrainAnalysis {

	public static void main(String[] args) {

		doAnalysis("sampled_relative_change_-0.000882-0.1.csv", "all");
		doAnalysis("sampled_relative_change_0.1-0.2.csv", "all");
		doAnalysis("sampled_relative_change_0.2-0.3.csv", "all");
		doAnalysis("sampled_relative_change_0.3-0.4.csv", "all");
		doAnalysis("sampled_relative_change_0.4-0.5.csv", "all");
		doAnalysis("sampled_relative_change_0.5-0.6.csv", "all");
		doAnalysis("sampled_relative_change_0.6-0.7.csv", "all");
		doAnalysis("sampled_relative_change_0.7-0.8.csv", "all");
		doAnalysis("sampled_relative_change_0.8-0.9.csv", "all");
		doAnalysis("sampled_relative_change_0.9-1.0.csv", "all");
		doAnalysis("sampled_relative_change_outliers.csv", "all");

		doAnalysis("sample_bin2_relative_change_-8.1e-05-0.025.csv", "all");
		doAnalysis("sample_bin2_relative_change_0.025-0.0499.csv", "all");
		doAnalysis("sample_bin2_relative_change_0.0499-0.0748.csv", "all");
		doAnalysis("sample_bin2_relative_change_0.0748-0.0997.csv", "all");
		doAnalysis("sample_bin2_relative_change_0.0997-0.125.csv", "all");
		doAnalysis("sample_bin2_relative_change_0.125-0.15.csv", "all");
		doAnalysis("sample_bin2_relative_change_0.15-0.174.csv", "all");
		doAnalysis("sample_bin2_relative_change_0.174-0.199.csv", "all");

		System.out.println("Done");
	}

	public static void doAnalysis(String clusterCsv, String className) {
		String rootFolder = "../../";
		String metamodelsFolder = rootFolder + "metamodels/";
		String inputFile = rootFolder + "metamodel_changes_analysis/" + clusterCsv;
		String outputFile = inputFile + ".analysis.txt";

		try (
				Reader reader = new FileReader(inputFile);
				CSVParser csvParser = new CSVParser(reader, CSVFormat.DEFAULT.withFirstRecordAsHeader());
				PrintWriter writer = new PrintWriter(new FileWriter(outputFile));) {

			int counter = 0;
			for (CSVRecord csvRecord : csvParser) {
				Map<String, Integer> diffCounts = new HashMap<>();

				try {
					MetamodelComparison mc = new MetamodelComparison();
					// left takes the new model role, so right is the "original"
					mc.compare(
							metamodelsFolder + csvRecord.get("duplicate_path"),
							metamodelsFolder + csvRecord.get("original_path"));

					Map<Match, List<Diff>> changesMap = mc.getChangesMap();

					writer.println(counter);
					writer.println(csvRecord.get("duplicate_path"));
					writer.println(csvRecord.get("original_path"));

					for (Entry<Match, List<Diff>> entry : changesMap.entrySet()) {
						if (className.equalsIgnoreCase("all") ||
								getAffectedType(entry.getKey()).getName().equals(className)) {

							for (Diff d : entry.getValue()) {
								countFeatureDiff(diffCounts, d);
							}
						}
					}
					// in the "all case", report other diffs as well (add, delete, move)
					if (className.equalsIgnoreCase("all")) {
						for (Diff d : mc.getOtherDiffs()) {
							countFeatureDiff(diffCounts, d);
						}
					}
					writer.println("Left  (new) size: " + mc.getLeftSize());
					writer.println("Right (old) size: " + mc.getRightSize());

					writer.println("Left  (new) size (ignoring annotations): " + mc.getLeftSize(true));
					writer.println("Right (old) size (ignoring annotations): " + mc.getRightSize(true));
					writer.println("---");

					writer.println("Left  (new) #EClasses: " + mc.getLeftElementCounts().getOrDefault(EcorePackage.Literals.ECLASS, 0));
					writer.println("Right (old) #EClasses: " + mc.getRightElementCounts().getOrDefault(EcorePackage.Literals.ECLASS, 0));
					writer.println("---");
					
					writer.println("Left  (new) Elem counts: " + convertAndSortMap(mc.getLeftElementCounts()));
					writer.println("Right (old) Elem counts: " + convertAndSortMap(mc.getRightElementCounts()));
					writer.println("---");

					writer.println("Number of differences: " + mc.getNumberOfDifferences());
					writer.println("Number of affected elements: " + mc.getNumberOfAffectedElements());
					writer.println("Number of affected annotations: " + mc.getNumberOfAffectedAnnotations());
					writer.println("Difference: " + (mc.getNumberOfAffectedElements() - mc.getNumberOfAffectedAnnotations()));
					writer.println("---");

					writer.println("Ratio of affected elements (not ignoring annotations): "
							+ (float) mc.getNumberOfAffectedElements() / mc.getRightSize());

					writer.println("Ratio of affected elements (ignoring annotations): "
							+ (float) (mc.getNumberOfAffectedElements() - mc.getNumberOfAffectedAnnotations()) / mc.getRightSize(true));

					writer.println("@@@@@@@@@@@@@@@@");

					writer.println("All diffs: " + sortMap(mc.getDiffCounts()));
					writer.println("Fine diffs: " + sortMap(diffCounts));
					writer.println("\n\n\n");
					

					mc.dispose();
					counter++;
				}
				catch (Exception e) {
					System.out.println(csvRecord.get("duplicate_path"));
					System.out.println(csvRecord.get("original_path"));
					System.out.println(e);
				}
			}
		}
		catch (IOException e) {
			e.printStackTrace();
		}
		System.out.println(clusterCsv);
	}

	public static EClass getAffectedType(Match m) {
		if (m.getLeft() != null) {
			return m.getLeft().eClass();
		}
		else {
			return m.getRight().eClass();
		}
	}

	public static void countFeatureDiff(Map<String, Integer> diffCounts, Diff d) {
		String key = d.getKind().getLiteral();
		if (d instanceof ReferenceChange) {
			ReferenceChange rc = (ReferenceChange) d;
			key += "-" + rc.getReference().getEContainingClass().getName() + "."
					+ rc.getReference().getName();
		}
		else if (d instanceof AttributeChange) {
			AttributeChange ac = (AttributeChange) d;
			key += "-" + ac.getAttribute().getEContainingClass().getName() + "."
					+ ac.getAttribute().getName();
		}
		else if (d instanceof ResourceAttachmentChange) {
			ResourceAttachmentChange rac = (ResourceAttachmentChange) d;
			Match m = rac.getMatch();
			key += "-ResourceAttachment" + ".";
			if (d.getKind() == DifferenceKind.ADD) {
				key += m.getLeft().eClass().getName();
			}
			else if (d.getKind() == DifferenceKind.DELETE) {
				key += m.getRight().eClass().getName();
			}
		}
		diffCounts.put(key, diffCounts.getOrDefault(key, 0) + 1);
	}

	public static Map<String, Integer> sortMap(Map<String, Integer> map) {
		Map<String, Integer> sortedMap = map.entrySet()
				.stream()
				.sorted(Map.Entry.comparingByValue(Comparator.reverseOrder()))
				.collect(Collectors.toMap(
						Map.Entry::getKey,
						Map.Entry::getValue,
						(e1, e2) -> e1,
						LinkedHashMap::new // Preserve the order of sorted entries
				));
		return sortedMap;
	}

	public static Map<String, Integer> convertAndSortMap(Map<EClass, Integer> map) {
		Map<String, Integer> convertedMap = new HashMap<>();

		for (Entry<EClass, Integer> entry : map.entrySet()) {
			convertedMap.put(entry.getKey().getName(), entry.getValue());
		}
		return sortMap(convertedMap);
	}
}
