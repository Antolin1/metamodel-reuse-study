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
		
		Map<String, MetamodelComparison> closerComparisons = new HashMap<>();

		for (String metamodel : metamodels) {
			int minAffectedElements = Integer.MAX_VALUE;
			MetamodelComparison closerComparison = null;
			for (String otherMetamodel : metamodels) {
				if (metamodel.equals(otherMetamodel)) {
					continue;
				}
				MetamodelComparison mc = new MetamodelComparison();
				mc.compare(rootFolder + metamodel, rootFolder + otherMetamodel);
				mc.dispose();

				if (mc.getNumberOfAffectedElements() < minAffectedElements) {
					minAffectedElements = mc.getNumberOfAffectedElements();
					closerComparison = mc;
				}
			}
			closerComparisons.put(metamodel, closerComparison);
		}

		int cluster = 0;
		for (String metamodel : metamodels) {
			MetamodelComparison mc = closerComparisons.get(metamodel);
			
			System.out.println("********************************************");
			System.out.println("Cluster: " + cluster);
			cluster++;
			System.out.println("Metamodel: " + metamodel);
			System.out.println("Closer metamodel: " + mc.getRightPath());
			
			System.out.println("#elems left: " + mc.getLeftSize());
			System.out.println("#elems right: " + mc.getRightSize());
			System.out.println("#diffs: " + mc.getNumberOfDifferences());
			System.out.println("#affected elems: " + mc.getNumberOfAffectedElements());

			Map<String, Integer> diffCounts = mc.getDiffCounts();

			List<String> sortedKeys = new ArrayList<>(diffCounts.keySet());
			Collections.sort(sortedKeys);

			// Print the results
			for (String key : sortedKeys) {
				System.out.println(key + ": " + diffCounts.get(key));
			}
		}
	}

}
