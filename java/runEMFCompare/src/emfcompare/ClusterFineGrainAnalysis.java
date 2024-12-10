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

public class ClusterFineGrainAnalysis {

	public static void main(String[] args) {

		// macro/grouped clusters
		//		doAnalysis("macro_cluster0-structural-major-sample.csv", "all");
		//		doAnalysis("macro_cluster1-annotations-sample.csv", "all");
		//		doAnalysis("macro_cluster2-nonstructural-minor-sample.csv", "all");
		//		doAnalysis("macro_cluster3-package-sample.csv", "all");

		// fine-grain analysis of kmeans clusters
		//		for (int c = 0; c < 10; c++) {
		//			doAnalysis(String.format("kmeans-cluster%d-sample.csv", c), "all");
		//		}
		doAnalysis("structural-above-non-structural.csv", "all");
		doAnalysis("structural-below-non-structural.csv", "all");

		System.out.println("Done");
	}

	public static void doAnalysis(String clusterCsv, String className) {
		String rootFolder = "../../";
		String metamodelsFolder = rootFolder + "metamodels/";
		String inputFile = rootFolder + "feature_clusters/" + clusterCsv;
		String outputFile = rootFolder + "feature_clusters/" + clusterCsv + ".analysis.txt";

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
					writer.println("Left size: " + mc.getLeftSize());
					writer.println("Right size: " + mc.getRightSize());
					writer.println("All diffs: " + sortMap(mc.getDiffCounts()));
					writer.println("Fine diffs: " + sortMap(diffCounts));
					writer.println();

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
}
