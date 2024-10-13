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

		for (Entry<Integer, List<String>> entry : clusters.entrySet()) {
			System.out.println("*********************************************");
			System.out.println("Cluster " + entry.getKey());

			List<List<String>> pairs = getAllPairs(entry.getValue());

			for (List<String> pair : pairs) {
				String path = pair.get(0);
				String otherPath = pair.get(1);
				MetamodelComparison mc = new MetamodelComparison();
				mc.compare(rootFolder + path, rootFolder + otherPath);
				System.out.println(path);
				System.out.println(otherPath);
				System.out.println("#elems left: " + mc.getLeftSize());
				System.out.println("#elems right: " + mc.getRightSize());
				System.out.println("#diffs: " + mc.getNumberOfAffectedElements());
				System.out.println("#affected elems: " + mc.getNumberOfAffectedElements());

				Map<String, Integer> diffCounts = mc.getDiffCounts();

				List<String> sortedKeys = new ArrayList<>(diffCounts.keySet());
				Collections.sort(sortedKeys);

				// Print the results
				for (String key : sortedKeys) {
					System.out.println(key + ": " + diffCounts.get(key));
				}

				mc.dispose();
			}
		}
	}

	public static List<List<String>> getAllPairs(List<String> elements) {
		List<List<String>> pairs = new ArrayList<>();

		for (int i = 0; i < elements.size(); i++) {
			for (int j = i + 1; j < elements.size(); j++) {
				List<String> pair = new ArrayList<>();
				pair.add(elements.get(i));
				pair.add(elements.get(j));
				pairs.add(pair);
			}
		}

		return pairs;
	}
}
