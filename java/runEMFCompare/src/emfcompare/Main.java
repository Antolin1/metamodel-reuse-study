package emfcompare;

import java.io.BufferedWriter;
import java.io.FileWriter;
import java.io.IOException;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.util.ArrayList;
import java.util.List;

import org.eclipse.emf.common.util.URI;
import org.eclipse.emf.compare.Comparison;
import org.eclipse.emf.compare.Diff;
import org.eclipse.emf.compare.EMFCompare;
import org.eclipse.emf.compare.diff.DefaultDiffEngine;
import org.eclipse.emf.compare.diff.DiffBuilder;
import org.eclipse.emf.compare.diff.FeatureFilter;
import org.eclipse.emf.compare.diff.IDiffProcessor;
import org.eclipse.emf.compare.scope.DefaultComparisonScope;
import org.eclipse.emf.compare.scope.IComparisonScope;
import org.eclipse.emf.ecore.EStructuralFeature;
import org.eclipse.emf.ecore.resource.Resource;
import org.eclipse.emf.ecore.resource.impl.ResourceSetImpl;
import org.eclipse.emf.ecore.xmi.impl.EcoreResourceFactoryImpl;

public class Main {
	
	private static class Tuple {
		public int id;
		public int diffs;
		public Tuple(int id, int diffs) {
			super();
			this.id = id;
			this.diffs = diffs;
		}
		
	}
	
	private static final String PATH = "/home/antolin/projects/metamodel-reuse-study/metamodels";
	private static final String JDBC_URL = "jdbc:sqlite:/home/antolin/projects/metamodel-reuse-study/dup_network.db";
	private static final int lower = 70000;
	private static final int upper = 140000;
	private static final String OUTPUT = "/home/antolin/projects/metamodel-reuse-study/distances" + Integer.toString(lower) 
		+ "-" + Integer.toString(upper) + ".csv";
	
	public static int numberDiffs(String path1, String path2, EMFCompare comparator) {
		URI uri1 = URI.createFileURI(path1);
		URI uri2 = URI.createFileURI(path2);
		
		ResourceSetImpl resourceSet1 = new ResourceSetImpl();
		ResourceSetImpl resourceSet2 = new ResourceSetImpl();
		
		try {
			resourceSet1.getResource(uri1, true);
			resourceSet2.getResource(uri2, true);
			// rs2 -> rs1
			//IComparisonScope scope = EMFCompare.createDefaultScope(resourceSet1, resourceSet2);
			DefaultComparisonScope scope = new DefaultComparisonScope(resourceSet1, resourceSet2, null);
			Comparison comparison = comparator.compare(scope);
			List<Diff> differences = comparison.getDifferences();
			
			// unload resources
			resourceSet1.getResources().forEach(r -> r.unload());
			resourceSet2.getResources().forEach(r -> r.unload());
			return differences.size();
		} catch (Exception e) {
			return -1;
		}
		
		
		

		
	}
	
	public static void main(String[] args) throws SQLException, IOException {
		
		// EMF setup
		Resource.Factory.Registry.INSTANCE.getExtensionToFactoryMap().put("ecore", new EcoreResourceFactoryImpl());
		IDiffProcessor diffProcessor = new DiffBuilder();
		DefaultDiffEngine diffEngine = new DefaultDiffEngine(diffProcessor) {
			@Override
			protected FeatureFilter createFeatureFilter() {
				return new FeatureFilter() {

					@Override
					public boolean checkForOrderingChanges(EStructuralFeature feature) {
						return false;
					}
				};
			}
		};
		EMFCompare comparator = EMFCompare.builder().setDiffEngine(diffEngine).build();
		
		// database setup
		Connection connection = DriverManager.getConnection(JDBC_URL);
		String sqlQuery = "SELECT d.id as id, source.local_path as s, target.local_path as t FROM duplicates d JOIN metamodels "
				+ "source on source.id = d.m1 JOIN metamodels target on target.id = d.m2 "
				+ "WHERE d.id < " + Integer.toString(upper) + " AND d.id>= " + Integer.toString(lower);
		Statement statement = connection.createStatement();
		ResultSet resultSet = statement.executeQuery(sqlQuery);
		
		// iteration
		List<Tuple> toSave = new ArrayList<>();
		while (resultSet.next()) {
			String source = resultSet.getString("s");
			String target = resultSet.getString("t");
			int id = resultSet.getInt("id");
			
			System.out.println(id + ":" + source + " vs " + target);
			int diffs = numberDiffs(PATH + "/" + source, PATH + "/" + target, comparator);
			toSave.add(new Tuple(id, diffs));
		}
		
		//save to disk
		FileWriter fw = new FileWriter(OUTPUT);
		BufferedWriter writer = new BufferedWriter(fw);
		for (Tuple tuple : toSave) {
			writer.write(Integer.toString(tuple.id) +","+Integer.toString(tuple.diffs));
            writer.newLine();
		}
		writer.flush();
		connection.close();
	}
	
	

}
