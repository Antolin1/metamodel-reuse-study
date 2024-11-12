package emfcompare;

import java.io.File;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

import org.eclipse.emf.common.util.URI;
import org.eclipse.emf.compare.AttributeChange;
import org.eclipse.emf.compare.Comparison;
import org.eclipse.emf.compare.Diff;
import org.eclipse.emf.compare.EMFCompare;
import org.eclipse.emf.compare.Match;
import org.eclipse.emf.compare.ReferenceChange;
import org.eclipse.emf.compare.ResourceAttachmentChange;
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

public class Test {
	

	public static void main(String[] args) {
		File file1 = new File("1forintos$mondo_test$model#Model.ecore");
		File file2 = new File("1forintos$mondo_test$model#Model2.ecore");
		URI uri1 = URI.createFileURI(file1.getAbsolutePath());
		URI uri2 = URI.createFileURI(file2.getAbsolutePath());
		
		//URI uri1 = URI.createFileURI("/home/antolin/eclipse-workspace-default/emfCompareExample/src/1forintos$mondo_test$model#Model.ecore");
		//URI uri2 = URI.createFileURI("/home/antolin/eclipse-workspace-default/emfCompareExample/src/1forintos$mondo_test$model#Model2.ecore");
		
		Resource.Factory.Registry.INSTANCE.getExtensionToFactoryMap().put("ecore", new EcoreResourceFactoryImpl());

		ResourceSetImpl resourceSet1 = new ResourceSetImpl();
		ResourceSetImpl resourceSet2 = new ResourceSetImpl();

		resourceSet1.getResource(uri1, true);
		resourceSet2.getResource(uri2, true);
		

		
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
		
		// rs2 -> rs1
		IComparisonScope scope = new DefaultComparisonScope(resourceSet1, resourceSet2, null);
		Comparison comparison = EMFCompare.builder().setDiffEngine(diffEngine).build().compare(scope);

		List<Diff> differences = comparison.getDifferences();

		for(Diff d: differences)
	    {
	      System.out.println("KIND: "+d.getKind() + " " + d.getClass());
	      if (d instanceof 	AttributeChange) {
	    		AttributeChange ac = (AttributeChange) d;
	    		System.out.println(ac.getValue());
			}
			else if (d instanceof ReferenceChange) {
				ReferenceChange rc = (ReferenceChange) d;
	    	  System.out.println(((ReferenceChange) d).getValue());
	    	  System.out.println(rc.getReference());
	      } else if (d instanceof ResourceAttachmentChange) {
	    	  ResourceAttachmentChange rac = (ResourceAttachmentChange) d;
	    	  System.out.println(rac.getResourceURI());
	      }
	      // System.out.println(d.getMatch());
	      System.out.println(d.getMatch().getLeft());
	      System.out.println(d.getMatch().getRight());
	      //System.out.println(d.getMatch().getAllSubmatches());
	      System.out.println("----------");
	    }  
		
		System.out.println("Number of differences: " + getNumberOfDifferences(comparison));
		System.out.println("Number of affected elements: " + getNumberOfAffectedElements(comparison));



	}

	public static int getNumberOfAffectedElements(Comparison comparison) {
		Set<Match> changedElements = new HashSet<>();
		
		// a change diff is contained in a match of the same element
		// additions, deletions and movements are placed in a match of the eContainer
		//   that holds the added, deleted or moved element, must be counted separatedly
		int otherDiffs = 0;

		for (Diff d : comparison.getDifferences()) {
			switch (d.getKind()) {
				case CHANGE:
					changedElements.add((Match) d.eContainer());
					break;
				case ADD:
				case DELETE:
				case MOVE:
					otherDiffs += 1;
				}
		}
		return changedElements.size() + otherDiffs;
	}

	public static int getNumberOfDifferences(Comparison comparison) {
		return comparison.getDifferences().size();
	}

}
