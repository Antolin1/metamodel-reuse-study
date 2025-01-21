package emfcompare;

import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.io.PrintWriter;
import java.io.Reader;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.TreeSet;

import org.apache.commons.csv.CSVFormat;
import org.apache.commons.csv.CSVParser;
import org.apache.commons.csv.CSVPrinter;
import org.apache.commons.csv.CSVRecord;

public class ClusterStarsAnalysisIntra {

	public static void main(String[] args) {
		String rootFolder = "../../";
		String metamodelsFolder = rootFolder + "metamodels/";
		String csvFile = rootFolder + "cluster_stars-intra.csv";
		String outputCsv = rootFolder + "feature_clusters/cluster_stars_with_concrete_features-intra.csv";

		// the set of diff features is calculated first, and then the dataset is generated
		Set<String> features = new TreeSet<>();
		Map<String, MetamodelComparison> comparisons = new HashMap<>();

		int repo = 0;
		try (Reader reader = new FileReader(csvFile);
				CSVParser csvParser = new CSVParser(reader, CSVFormat.DEFAULT.withFirstRecordAsHeader());) {

			for (CSVRecord csvRecord : csvParser) {
				int currentRepo = Integer.parseInt(csvRecord.get("repo"));
				if (currentRepo > repo) {
					repo = currentRepo;
					System.out.println(repo);
				}

				try {
					MetamodelComparison mc = new MetamodelComparison();
					mc.setUseAllTypes(true);
					// left takes the new model role, so right is the "original"
					mc.compare(
							metamodelsFolder + csvRecord.get("duplicate_path"),
							metamodelsFolder + csvRecord.get("original_path"));
					mc.dispose();

					features.addAll(FeaturesUtil.getConcreteFeatures(mc));
					comparisons.put(getKey(csvRecord), mc);
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

		System.out.println(features);

		String[] metadata = { "repo", "repo_name", "cluster", "original", "original_path", "duplicate", "duplicate_path", "affected_elements" };
		String[] featuresArray = features.toArray(new String[0]);

		String[] header = new String[metadata.length + featuresArray.length];

		System.arraycopy(metadata, 0, header, 0, metadata.length);
		System.arraycopy(featuresArray, 0, header, metadata.length, featuresArray.length);

		try (
				Reader reader = new FileReader(csvFile);
				CSVParser csvParser = new CSVParser(reader, CSVFormat.DEFAULT.withFirstRecordAsHeader());
				PrintWriter writer = new PrintWriter(new FileWriter(outputCsv));
				CSVPrinter csvPrinter = new CSVPrinter(writer, CSVFormat.DEFAULT.withHeader(header))) {

			repo = 0;
			for (CSVRecord csvRecord : csvParser) {

				int currentRepo = Integer.parseInt(csvRecord.get("repo"));
				if (currentRepo > repo) {
					repo = currentRepo;
					System.out.println(repo);
				}

				List<String> newRecord = new ArrayList<>(header.length);

				newRecord.add(csvRecord.get("repo"));
				newRecord.add(csvRecord.get("repo_name"));
				newRecord.add(csvRecord.get("cluster"));
				newRecord.add(csvRecord.get("original"));
				newRecord.add(csvRecord.get("original_path"));
				newRecord.add(csvRecord.get("duplicate"));
				newRecord.add(csvRecord.get("duplicate_path"));

				MetamodelComparison mc = comparisons.get(getKey(csvRecord));

				newRecord.add("" + mc.getNumberOfAffectedElements());

				Set<String> foundFeatures = FeaturesUtil.getConcreteFeatures(mc);

				for (String feature : features) {
					String value = "0";
					if (foundFeatures.contains(feature)) {
						value = "1";
					}
					newRecord.add(value);
				}

				csvPrinter.printRecord(newRecord);
			}
		}
		catch (IOException e) {
			e.printStackTrace();
		}
	}

	public static String getKey(CSVRecord row) {
		return row.get("duplicate_path") + "@" + row.get("original_path");
	}
}
