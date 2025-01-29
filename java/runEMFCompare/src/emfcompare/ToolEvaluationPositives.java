package emfcompare;

import java.io.FileReader;
import java.io.IOException;
import java.io.Reader;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Map.Entry;

import org.apache.commons.csv.CSVFormat;
import org.apache.commons.csv.CSVParser;
import org.apache.commons.csv.CSVRecord;

public class ToolEvaluationPositives {

	public static void main(String[] args) {
		String rootFolder = "../../tool_evaluation/";
		String csvFile = "positive.csv";

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
			cluster++;

			System.out.println("Representative: " + mc.getLeftPath());
			System.out.println("Most distant  : " + mc.getRightPath());

			System.out.println("#elems left: " + mc.getLeftSize());
			System.out.println("#elems right: " + mc.getRightSize());
			System.out.println("#diffs: " + mc.getNumberOfDifferences());
			System.out.println("#affected elems: " + mc.getNumberOfAffectedElements());
			System.out.println("distance:" + getDistance(mc));

			Map<String, Integer> diffCounts = mc.getDiffCounts();

			List<String> sortedKeys = new ArrayList<>(diffCounts.keySet());
			Collections.sort(sortedKeys);

			System.out.println("Counts:");
			for (String key : sortedKeys) {
				System.out.println(key + ": " + diffCounts.get(key));
			}

			System.out.println();
			System.out.println("Plain: " + FeaturesUtil.getPlainFeatures(mc));
			System.out.println("Concrete: " + FeaturesUtil.getConcreteFeatures(mc));
		}
	}

	public static double getDistance(MetamodelComparison mc) {
		return (double) mc.getNumberOfAffectedElements() / (double) (mc.getLeftSize() + mc.getRightSize());
	}

}
