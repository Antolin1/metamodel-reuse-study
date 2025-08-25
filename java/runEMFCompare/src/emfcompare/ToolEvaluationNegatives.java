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
 * picks the closest "negative clone" for each meta-model, this is, the meta-model
 * with the least number of differences that was not considered a clone.
 */
public class ToolEvaluationNegatives {

	public static void main(String[] args) {
		String rootFolder = "../../tool_evaluation/";
		String csvFile = "label_005_negative.csv";

		List<String> metamodels = new ArrayList<>();

		try (Reader reader = new FileReader(rootFolder + csvFile);
				CSVParser csvParser = new CSVParser(reader, CSVFormat.DEFAULT.withAllowMissingColumnNames());) {

			for (CSVRecord csvRecord : csvParser) {
				metamodels.add(csvRecord.get(0));
			}
		}
		catch (IOException e) {
			e.printStackTrace();
		}
		
		Map<String, MetamodelComparison> closestComparisons = new HashMap<>();

		System.out.println("representative,closest,duplicate_detector");
		for (String metamodel : metamodels) {
			double minDistance = Double.MAX_VALUE;
			MetamodelComparison closestComparison = null;
			String closestMM = "";
			for (String otherMetamodel : metamodels) {
				if (metamodel.equals(otherMetamodel)) {
					continue;
				}
				MetamodelComparison mc = new MetamodelComparison();
				mc.compare(rootFolder + metamodel, rootFolder + otherMetamodel);
				mc.dispose();

				double distance = getDistance(mc);
				if (distance < minDistance) {
					minDistance = distance;
					closestComparison = mc;
					closestMM = otherMetamodel;
				}
			}
			closestComparisons.put(metamodel, closestComparison);

			// "0" means the detector identified the other mm as a duplicate
			System.out.printf("%s,%s,%d\n", metamodel, closestMM, 0);
		}

		int cluster = 0;
		for (String metamodel : metamodels) {
			MetamodelComparison mc = closestComparisons.get(metamodel);
			
			System.out.println("********************************************");
			System.out.println("Cluster: " + cluster);
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
		return (double) mc.getNumberOfAffectedElements() / (double) mc.getRightSize();
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
