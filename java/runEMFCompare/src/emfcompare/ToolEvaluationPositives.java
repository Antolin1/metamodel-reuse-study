package emfcompare;

import java.io.FileReader;
import java.io.IOException;
import java.io.Reader;
import java.util.ArrayList;
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
 * Script used to evaluate the performace of the clone detector. This script
 * picks the farthest "positive clone" for each meta-model, this is, the meta-model
 * with the largest number of differences that was considered a clone.
 */
public class ToolEvaluationPositives {

	public static void main(String[] args) {
		String rootFolder = "../../tool_evaluation/";
		String csvFile = "label_005_positive.csv";

		Map<Integer, List<String>> clusters = new HashMap<>();

		try (Reader reader = new FileReader(rootFolder + csvFile);
				CSVParser csvParser = new CSVParser(reader, CSVFormat.DEFAULT.withAllowMissingColumnNames())) {

			for (CSVRecord csvRecord : csvParser) {
				String path = csvRecord.get(0);
				int cluster = Integer.parseInt(csvRecord.get(1));

				if (!clusters.containsKey(cluster)) {
					clusters.put(cluster, new ArrayList<>());
				}
				clusters.get(cluster).add(path);
			}
		}
		catch (IOException e) {
			e.printStackTrace();
		}

		List<MetamodelComparison> distantComparisons = new ArrayList<>();
		System.out.println("representative,most_distant,duplicate_detector");
		for (Entry<Integer, List<String>> entry : clusters.entrySet()) {

			List<String> metamodels = entry.getValue();
			String representative = metamodels.get(0);

			String mostDistantMM = "";
			double maxDistance = -1.0;
			MetamodelComparison mostDistantComparison = null;

			for (int mm = 1; mm < metamodels.size(); mm++) {
				String otherMM = metamodels.get(mm);
				MetamodelComparison mc = new MetamodelComparison();
				mc.setUseAllTypes(true);
				mc.compare(rootFolder + representative, rootFolder + otherMM);

				double distance = getDistance(mc);
				if (distance > maxDistance) {
					mostDistantMM = otherMM;
					maxDistance = distance;
					mostDistantComparison = mc;
				}

				mc.dispose();
			}
			distantComparisons.add(mostDistantComparison);

			// "1" means the detector identified the other mm as a duplicate
			System.out.printf("%s,%s,%d\n", representative, mostDistantMM, 1);
		}

		System.out.println();
		System.out.println("************** Comparisons ****************");

		int cluster = 0;
		for (MetamodelComparison mc : distantComparisons) {
			System.out.println("\nCluster: " + cluster);
			System.out.println();
			cluster++;

			System.out.println(mc.getLeftPath());
			System.out.println(mc.getRightPath());

			System.out.println("Left  (new) size: " + mc.getLeftSize());
			System.out.println("Right (old) size: " + mc.getRightSize());

			System.out.println("Left  (new) size (ignoring annotations): " + mc.getLeftSize(true));
			System.out.println("Right (old) size (ignoring annotations): " + mc.getRightSize(true));
			System.out.println("---");

			System.out.println("Left  (new) #EClasses: " + mc.getLeftElementCounts().getOrDefault(EcorePackage.Literals.ECLASS, 0));
			System.out.println("Right (old) #EClasses: " + mc.getRightElementCounts().getOrDefault(EcorePackage.Literals.ECLASS, 0));
			System.out.println("---");

			System.out.println("Left  (new) Elem counts: " + convertAndSortMap(mc.getLeftElementCounts()));
			System.out.println("Right (old) Elem counts: " + convertAndSortMap(mc.getRightElementCounts()));
			System.out.println("---");

			System.out.println("Number of differences: " + mc.getNumberOfDifferences());
			System.out.println("Number of affected elements: " + mc.getNumberOfAffectedElements());
			System.out.println("Number of affected annotations: " + mc.getNumberOfAffectedAnnotations());
			System.out.println("Difference: " + (mc.getNumberOfAffectedElements() - mc.getNumberOfAffectedAnnotations()));
			System.out.println("---");
			System.out.println("Number of package contents movements: " + mc.getNumberOfPackageContentsMovements());
			System.out.println("---");

			System.out.println("Ratio of affected elements (not ignoring annotations): "
					+ (double) mc.getNumberOfAffectedElements() / mc.getRightSize());

			System.out.println("Ratio of affected elements (ignoring annotations): "
					+ (double) (mc.getNumberOfAffectedElements() - mc.getNumberOfAffectedAnnotations()) / mc.getRightSize(true));

			System.out.println("@@@@@@@@@@@@@@@@");

			Map<String, Integer> diffCounts = new HashMap<>();
			for (Entry<Match, List<Diff>> entry : mc.getChangesMap().entrySet()) {
				for (Diff d : entry.getValue()) {
					countFeatureDiff(diffCounts, d);
				}
			}
			for (Diff d : mc.getOtherDiffs()) {
				countFeatureDiff(diffCounts, d);
			}

			System.out.println("All diffs: " + sortMap(mc.getDiffCounts()));
			System.out.println("Fine diffs: " + sortMap(diffCounts));
			System.out.println("\n\n\n");
		}
	}

	public static double getDistance(MetamodelComparison mc) {
		return (double) mc.getNumberOfAffectedElements() / (double) (mc.getRightSize());
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

}
