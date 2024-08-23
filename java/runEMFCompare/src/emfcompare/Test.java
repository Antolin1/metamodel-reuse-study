package emfcompare;

import java.io.File;
import java.util.List;

import org.eclipse.emf.common.util.URI;
import org.eclipse.emf.compare.AttributeChange;
import org.eclipse.emf.compare.Comparison;
import org.eclipse.emf.compare.Diff;
import org.eclipse.emf.compare.EMFCompare;
import org.eclipse.emf.compare.ReferenceChange;
import org.eclipse.emf.compare.ResourceAttachmentChange;
import org.eclipse.emf.compare.diff.DefaultDiffEngine;
import org.eclipse.emf.compare.diff.DiffBuilder;
import org.eclipse.emf.compare.diff.FeatureFilter;
import org.eclipse.emf.compare.diff.IDiffProcessor;
import org.eclipse.emf.compare.internal.spec.ReferenceChangeSpec;
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
		IComparisonScope scope = EMFCompare.createDefaultScope(resourceSet1, resourceSet2);
		Comparison comparison = EMFCompare.builder().setDiffEngine(diffEngine).build().compare(scope);

		List<Diff> differences = comparison.getDifferences();
		
		for(Diff d: differences)
	    {
	      System.out.println("KIND: "+d.getKind() + " " + d.getClass());
	      if (d instanceof 	AttributeChange) {
	    		AttributeChange ac = (AttributeChange) d;
	    		System.out.println(ac.getValue());
	      } else if (d instanceof ReferenceChangeSpec) {
	    	  ReferenceChangeSpec rc = (ReferenceChangeSpec) d;
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
		
		System.out.println(differences.size());


	}

}
