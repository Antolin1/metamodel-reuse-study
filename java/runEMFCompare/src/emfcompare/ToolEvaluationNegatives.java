package emfcompare;

import java.io.FileReader;
import java.io.IOException;
import java.io.Reader;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import org.apache.commons.csv.CSVFormat;
import org.apache.commons.csv.CSVParser;
import org.apache.commons.csv.CSVRecord;

/**
 * Script used to evaluate the performace of the clone detector. This script
 * picks the closest "negative clone" for each meta-model, this is, the meta-model
 * with the least number of differences that was not considered a clone.
 */
public class ToolEvaluationNegatives {

	public static void main(String[] args) {
		String rootFolder = "../../tool_evaluation/";
		String csvFile = "negative.csv";

		List<String> metamodels = new ArrayList<>();

		try (Reader reader = new FileReader(rootFolder + csvFile);
				CSVParser csvParser = new CSVParser(reader, CSVFormat.DEFAULT.withFirstRecordAsHeader());) {

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
			System.out.println("Metamodel: " + mc.getLeftPath());
			System.out.println("Closest  : " + mc.getRightPath());

			System.out.println("#elems left: " + mc.getLeftSize());
			System.out.println("#elems right: " + mc.getRightSize());
			System.out.println("#diffs: " + mc.getNumberOfDifferences());
			System.out.println("#affected elems: " + mc.getNumberOfAffectedElements());
			System.out.println("distance:" + getDistance(mc));

			Map<String, Integer> diffCounts = mc.getDiffCounts();

			List<String> sortedKeys = new ArrayList<>(diffCounts.keySet());
			Collections.sort(sortedKeys);

			// Print the results
			for (String key : sortedKeys) {
				System.out.println(key + ": " + diffCounts.get(key));
			}
			System.out.println();
		}
	}

	public static double getDistance(MetamodelComparison mc) {
		return (double) mc.getNumberOfAffectedElements() / (double) (mc.getLeftSize() + mc.getRightSize());
	}
}
