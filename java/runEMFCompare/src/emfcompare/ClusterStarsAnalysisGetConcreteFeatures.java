package emfcompare;

import java.io.FileReader;
import java.io.IOException;
import java.io.Reader;
import java.util.ArrayList;
import java.util.List;
import java.util.Set;
import java.util.TreeSet;

import org.apache.commons.csv.CSVFormat;
import org.apache.commons.csv.CSVParser;
import org.apache.commons.csv.CSVRecord;

public class ClusterStarsAnalysisGetConcreteFeatures {

	public static void main(String[] args) {
		String rootFolder = "../../";
		String metamodelsFolder = rootFolder + "metamodels/";
		String csvFile = rootFolder + "feature_clusters/cluster_stars.csv";

		Set<String> features = new TreeSet<>();

		int cluster = 0;
		try (Reader reader = new FileReader(csvFile);
				CSVParser csvParser = new CSVParser(reader, CSVFormat.DEFAULT.withFirstRecordAsHeader());) {

			List<MetamodelComparison> comparisons = new ArrayList<>();

			for (CSVRecord csvRecord : csvParser) {
				if (cluster != Integer.parseInt(csvRecord.get("cluster"))) {
					cluster++;
					System.out.println(cluster);
				}

				try {
					MetamodelComparison mc = new MetamodelComparison();
					mc.setUseAllTypes(true);
					// left takes the new model role, so right is the "original"
					mc.compare(
							metamodelsFolder + csvRecord.get("duplicate_path"),
							metamodelsFolder + csvRecord.get("original_path"));
					mc.dispose();

					comparisons.add(mc);
					features.addAll(FeaturesUtil.getConcreteFeatures(mc));
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
	}
}
