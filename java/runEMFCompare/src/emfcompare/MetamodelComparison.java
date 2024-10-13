package emfcompare;

import java.io.File;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
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
import org.eclipse.emf.compare.diff.IDiffEngine;
import org.eclipse.emf.compare.diff.IDiffProcessor;
import org.eclipse.emf.compare.scope.DefaultComparisonScope;
import org.eclipse.emf.compare.scope.IComparisonScope;
import org.eclipse.emf.ecore.EClass;
import org.eclipse.emf.ecore.EClassifier;
import org.eclipse.emf.ecore.EGenericType;
import org.eclipse.emf.ecore.EObject;
import org.eclipse.emf.ecore.EStructuralFeature;
import org.eclipse.emf.ecore.ETypedElement;
import org.eclipse.emf.ecore.resource.Resource;
import org.eclipse.emf.ecore.resource.ResourceSet;
import org.eclipse.emf.ecore.resource.impl.ResourceSetImpl;
import org.eclipse.emf.ecore.util.EcoreUtil;
import org.eclipse.emf.ecore.xmi.impl.EcoreResourceFactoryImpl;

public class MetamodelComparison {

	private static IDiffEngine diffEngine;
	protected Comparison comparison;
	protected int leftSize, rightSize;

	protected ResourceSet leftRS, rightRS;

	protected Map<String, Integer> diffCounts;
	protected int numberOfAffectedElements;

	static {
		Resource.Factory.Registry.INSTANCE.getExtensionToFactoryMap().put("ecore", new EcoreResourceFactoryImpl());

		IDiffProcessor diffProcessor = new DiffBuilder();
		diffEngine = new DefaultDiffEngine(diffProcessor) {

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
	}

	public static void main(String[] args) {

		MetamodelComparison mc = new MetamodelComparison();

		String rootFolder = "../../tool_evaluation/";

		//		String left = "manualDomains/466_008_108_States--1035737706.ecore";
		//		String right = "manualDomains/467_008_109_States--1687339431.ecore";

		String left = "manualDomains/475_008_117_SText--1184500197.ecore";
		String right = "manualDomains/488_008_130_SText-137906684.ecore";

		//		String left = "manualDomains/475mini.ecore";
		//		String right = "manualDomains/488mini.ecore";

		//		String left = "manualDomains/513_008_155_UmlState-690565703.ecore";
		//		String right = "manualDomains/512_008_154_UmlState--157654801.ecore";

		mc.compare(rootFolder + left, rootFolder + right);

		for (Diff d : mc.getComparison().getDifferences()) {
			System.out.println(d);
			if (d instanceof AttributeChange) {
				AttributeChange ac = (AttributeChange) d;
				System.out.println("New value (left): " + ac.getValue());
			}
			else if (d instanceof ReferenceChange) {
				ReferenceChange rc = (ReferenceChange) d;
				System.out.println("New value (left): " + rc.getValue());
			}
			else if (d instanceof ResourceAttachmentChange) {
				System.out.println("RESOURCE ATTACHMENT");
				ResourceAttachmentChange rac = (ResourceAttachmentChange) d;
				System.out.println(rac.getResourceURI());
			}
			System.out.println("Left match: " + d.getMatch().getLeft());
			System.out.println("Right match: " + d.getMatch().getRight());
			System.out.println("----------------------------------------------");
		}

		System.out.println("Number of differences: " + mc.getNumberOfDifferences());
		System.out.println("Number of affected elements: " + mc.getNumberOfAffectedElements());
		System.out.println("Left size: " + mc.getLeftSize());
		System.out.println("Right size: " + mc.getRightSize());

		System.out.println("@@@@@@@@@@@@@@@@");
		Map<String, Integer> diffCounts = mc.getDiffCounts();

		List<String> sortedKeys = new ArrayList<>(diffCounts.keySet());
		Collections.sort(sortedKeys);

		// Print the results
		for (String key : sortedKeys) {
			System.out.println(key + ": " + diffCounts.get(key));
		}

		mc.dispose();
	}

	public Map<String, Integer> getDiffCounts() {
		return diffCounts;
	}

	public MetamodelComparison() {
	}

	public void compare(String leftPath, String rightPath) {

		URI leftUri = URI.createFileURI(new File(leftPath).getAbsolutePath());
		URI rightUri = URI.createFileURI(new File(rightPath).getAbsolutePath());

		leftRS = new ResourceSetImpl();
		rightRS = new ResourceSetImpl();

		Resource leftResource = leftRS.getResource(leftUri, true);
		Resource rightResource = rightRS.getResource(rightUri, true);

		leftSize = countAllElements(leftResource);
		rightSize = countAllElements(rightResource);

		// left is always considered the new version (e.g. new elements in left
		// are additions, elements only appearing in right are considered deletions)
		IComparisonScope scope = new DefaultComparisonScope(leftResource, rightResource, null);

		comparison = EMFCompare.builder().setDiffEngine(diffEngine).build().compare(scope);
		processDifferences();
	}

	public int getNumberOfAffectedElements() {
		return numberOfAffectedElements;
	}

	protected void processDifferences() {
		boolean shouldCountFeatureDiff;


		// a change diff is contained in a match of the same element
		// additions and deletions have special cases that are treated below
		// moves are mostly of eContained elements
		Set<Match> changedElements = new HashSet<>();
		int otherDiffs = 0;

		diffCounts = new HashMap<>();

		for (Diff d : comparison.getDifferences()) {
			shouldCountFeatureDiff = false;

			switch (d.getKind()) {
			case CHANGE:
				if (d instanceof ReferenceChange) {
					ReferenceChange rc = (ReferenceChange) d;
					if (rc.getReference().getName().equals("eType")) {
						Match m = d.getMatch();
						// avoid counting type change when it happens with add/delete
						// otherwise one change gets counted twise
						// a side of the match missing -> added/deleted element
						if (m.getLeft() != null && m.getRight() != null) {
							if (!isProxyTypeDifference(rc)) {
								shouldCountFeatureDiff = true;
							}
						}
					}
				}
				else {
					shouldCountFeatureDiff = true;
				}

				if (shouldCountFeatureDiff) {
					changedElements.add((Match) d.eContainer());
				}
				break;

			case ADD:
			case DELETE:
				if (d instanceof ReferenceChange) {
					ReferenceChange rc = (ReferenceChange) d;
					if (rc.getReference().isContainment()) {
						otherDiffs += 1; // alternative way of counting because the matched elements are the containers
						shouldCountFeatureDiff = true;
					}
					else {
						// adds can happen in multi-valued non-containment refs
						// e.g. supertypes. These are considered changes of the container
						// only if the container has not been added/deleted (same issue as with eType)

						Match m = d.getMatch();
						if (m.getLeft() != null && m.getRight() != null) {
							if (!(rc.getReference().getName().equals("eSuperTypes") && isProxySuperTypeDifference(rc))) {
								changedElements.add(d.getMatch());
								shouldCountFeatureDiff = true;
							}
						}
					}
				}
				else {
					// TODO: resource attachments change
					//					System.out.println("Does this happen?" + d);
				}
				break;

			case MOVE:
				if (d instanceof ReferenceChange) {
					ReferenceChange rc = (ReferenceChange) d;
					if (rc.getReference().isContainment()) {
						otherDiffs += 1; // alternative way of counting because the matched elements are the containers
						shouldCountFeatureDiff = true;
					}
					else {
						System.out.println("THIS SHOULD NOT HAPPEN: " + rc.getReference());
					}
				}
			}
			if (shouldCountFeatureDiff) {
				countFeatureDiff(d);
			}
		}
		numberOfAffectedElements = changedElements.size() + otherDiffs;
	}

	/**
	 * Avoids counting differences caused by one of the sides using an eproxy supertype
	 */
	protected boolean isProxySuperTypeDifference(ReferenceChange rc) {
		Match m = rc.getMatch();

		EClass left = (EClass) m.getLeft();
		EClass right = (EClass) m.getRight();

		Iterator<EClass> leftSupertypes = left.getESuperTypes().iterator();
		Iterator<EClass> rightSupertypes = right.getESuperTypes().iterator();
		while (leftSupertypes.hasNext() && rightSupertypes.hasNext()) {
			if (leftSupertypes.next().eIsProxy() != rightSupertypes.next().eIsProxy()) {
				return true;
			}
		}
		return false;
	}

	/**
	 * Avoids counting differences caused by one of the sides using an eproxy type
	 * (referenced metamodels are not loaded for comparison)
	 */
	protected boolean isProxyTypeDifference(ReferenceChange rc) {
		Match m = rc.getMatch();

		EClassifier leftType = ((ETypedElement) m.getLeft()).getEType();
		EClassifier rightType = ((ETypedElement) m.getRight()).getEType();

		return leftType.eIsProxy() != rightType.eIsProxy();
	}

	protected void countFeatureDiff(Diff d) {
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
		diffCounts.put(key, diffCounts.getOrDefault(key, 0) + 1);
	}

	public int getNumberOfDifferences() {
		return comparison.getDifferences().size();
	}

	public Comparison getComparison() {
		return comparison;
	}

	public int countAllElements(Resource resource) {
		int count = 0;

		// Use EcoreUtil to get all contents in the resource
		Iterator<EObject> allContents = EcoreUtil.getAllContents(resource.getContents(), false);

		while (allContents.hasNext()) {
			EObject elem = allContents.next();
			if (!(elem instanceof EGenericType)) {
				count++; // Increment for each element				
			}
		}

		return count;
	}

	public int getLeftSize() {
		return leftSize;
	}

	public int getRightSize() {
		return rightSize;
	}

	public void dispose() {
		leftRS.getResources().forEach(r -> r.unload());
		rightRS.getResources().forEach(r -> r.unload());
		comparison = null;
	}
}
