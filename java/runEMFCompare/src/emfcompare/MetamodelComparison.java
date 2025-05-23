package emfcompare;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.HashMap;
import java.util.Iterator;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

import org.eclipse.emf.common.util.URI;
import org.eclipse.emf.compare.AttributeChange;
import org.eclipse.emf.compare.Comparison;
import org.eclipse.emf.compare.Diff;
import org.eclipse.emf.compare.DifferenceKind;
import org.eclipse.emf.compare.EMFCompare;
import org.eclipse.emf.compare.Match;
import org.eclipse.emf.compare.ReferenceChange;
import org.eclipse.emf.compare.ResourceAttachmentChange;
import org.eclipse.emf.compare.diff.DefaultDiffEngine;
import org.eclipse.emf.compare.diff.DiffBuilder;
import org.eclipse.emf.compare.diff.FeatureFilter;
import org.eclipse.emf.compare.diff.IDiffEngine;
import org.eclipse.emf.compare.diff.IDiffProcessor;
import org.eclipse.emf.compare.match.IMatchEngine;
import org.eclipse.emf.compare.match.impl.MatchEngineFactoryImpl;
import org.eclipse.emf.compare.match.impl.MatchEngineFactoryRegistryImpl;
import org.eclipse.emf.compare.scope.DefaultComparisonScope;
import org.eclipse.emf.compare.scope.IComparisonScope;
import org.eclipse.emf.compare.utils.UseIdentifiers;
import org.eclipse.emf.ecore.EClass;
import org.eclipse.emf.ecore.EClassifier;
import org.eclipse.emf.ecore.EObject;
import org.eclipse.emf.ecore.EStructuralFeature;
import org.eclipse.emf.ecore.ETypedElement;
import org.eclipse.emf.ecore.resource.Resource;
import org.eclipse.emf.ecore.resource.ResourceSet;
import org.eclipse.emf.ecore.resource.impl.ResourceSetImpl;
import org.eclipse.emf.ecore.util.EcoreUtil;
import org.eclipse.emf.ecore.xmi.impl.EcoreResourceFactoryImpl;

/**
 * Allows comparing two meta-models
 */
public class MetamodelComparison {

	private static IDiffEngine diffEngine;
	protected Comparison comparison;
	protected int leftSize, rightSize;

	/**
	 * Disable cutoff and subordinate types
	 */
	protected boolean useAllTypes = false;

	protected ResourceSet leftRS, rightRS;

	protected Map<String, Integer> diffCounts = new HashMap<>();
	protected int numberOfDifferences;
	protected int numberOfAffectedElements;

	// groups changes to the same model element or to the relevant parent
	protected Map<Match, List<Diff>> changesMap = new HashMap<>();

	// other diffs that are not changes
	protected List<Diff> otherDiffs = new ArrayList<>();

	protected String leftPath, rightPath;

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

		//		String rootFolder = "../../tool_evaluation/";
		String rootFolder = "../../metamodels/";

		String left = null;
		String right = null;

		try (BufferedReader br = new BufferedReader(new FileReader("compare.txt"))) {
			left = br.readLine();
			right = br.readLine();
		}
		catch (IOException e) {
			e.printStackTrace();
		}

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

		System.out.println(sortMap(diffCounts));

		mc.dispose();
	}

	public static Map<String, Integer> sortMap(Map<String, Integer> map) {
		Map<String, Integer> sortedMap = map.entrySet()
				.stream()
				.sorted(Map.Entry.comparingByValue(Comparator.reverseOrder()))
				.collect(Collectors.toMap(
						Map.Entry::getKey,
						Map.Entry::getValue,
						(e1, e2) -> e1,
						LinkedHashMap::new // Preserve the order of sorted entries
				));
		return sortedMap;
	}

	public Map<String, Integer> getDiffCounts() {
		return diffCounts;
	}

	public MetamodelComparison() {
	}

	public void compare(String leftPath, String rightPath) {

		this.leftPath = leftPath;
		this.rightPath = rightPath;

		URI leftUri = URI.createFileURI(new File(leftPath).getAbsolutePath());
		URI rightUri = URI.createFileURI(new File(rightPath).getAbsolutePath());

		leftRS = new ResourceSetImpl();
		rightRS = new ResourceSetImpl();

		Resource leftResource = leftRS.getResource(leftUri, true);
		Resource rightResource = rightRS.getResource(rightUri, true);

		leftSize = countAllElements(leftResource);
		rightSize = countAllElements(rightResource);

		// ignore xmi:ids to avoid issues when one side has them, but the other does not
		IMatchEngine.Factory matchEngineFactory = new MatchEngineFactoryImpl(UseIdentifiers.NEVER);
		matchEngineFactory.setRanking(20);
		IMatchEngine.Factory.Registry matchEngineRegistry = new MatchEngineFactoryRegistryImpl();
		matchEngineRegistry.add(matchEngineFactory);

		EMFCompare comparator = EMFCompare.builder()
				.setMatchEngineFactoryRegistry(matchEngineRegistry)
				.setDiffEngine(diffEngine)
				.build();

		// left is always considered the new version (e.g. new elements in left
		// are additions, elements only appearing in right are considered deletions)
		IComparisonScope scope = new DefaultComparisonScope(leftResource, rightResource, null);

		comparison = comparator.compare(scope);
		processDifferences();
	}

	public int getNumberOfAffectedElements() {
		return numberOfAffectedElements;
	}

	protected void processDifferences() {
		numberOfDifferences = comparison.getDifferences().size();


		// a change diff is contained in a match of the same element
		// additions and deletions have special cases that are treated below
		// moves are mostly of eContained elements

		int otherDiffsCounter = 0;

		for (Diff d : comparison.getDifferences()) {

			switch (d.getKind()) {
			case CHANGE:
				boolean shouldCountChange = false;
				if (d instanceof ReferenceChange) {
					ReferenceChange rc = (ReferenceChange) d;
					// avoid counting type change when it happens with add/delete
					// otherwise one change gets counted twice
					// a side of the match missing -> added/deleted element
					if (existLeftAndRight(d.getMatch())) {
						if (isSubordinateType(d)) {
							Match m = getFirstNotSubordinateParent(d);
							if (m != null) {
								registerChange(m, d);
							}
						}
						else if (rc.getReference().getName().equals("eType")) {
							if (!isProxyTypeDifference(rc)) {
								shouldCountChange = true;
							}
						}
						else {
							shouldCountChange = true;
						}
					}
				}
				else {
					if (isSubordinateType(d)) {
						// count the change, but for the container of this match
						// e.g. the Annotation that holds a map entry that has changed
						Match m = getFirstNotSubordinateParent(d);
						if (m != null) {
							registerChange(m, d);
						}
					}
					else {
						// normal attribute changes
						shouldCountChange = true;
					}
				}

				if (shouldCountChange) {
					registerChange(d.getMatch(), d);
				}
				break;

			case ADD:
			case DELETE:
				if (isCutoffType(d)) {
					// ignore add/del, treat it as a change of the cutoff type
					if (existLeftAndRight(d.getMatch())) {
						registerChange(d.getMatch(), d);
					}
				}
				else if (d instanceof ReferenceChange) {
					ReferenceChange rc = (ReferenceChange) d;
					if (rc.getReference().isContainment()) {
						// check here if the type is a subordinate one
						// if it is, count as a change of the container

						if (isSubordinateType(d)) {
							// we treat this as a changed container
							// we have to search for the first container that is not a subordinate
							Match m = getFirstNotSubordinateParent(d);
							if (m != null) {
								registerChange(m, d);
							}
						}
						else {
							countFeatureDiff(d);
							otherDiffsCounter += 1; // alternative way of counting because the matched elements are the containers
							otherDiffs.add(d);
						}
					}
					else {
						// adds can happen in multi-valued non-containment refs
						// e.g. supertypes. These are considered changes of the container
						// only if the container has not been added/deleted (same issue as with eType)

						if (existLeftAndRight(d.getMatch())) {
							if (!(rc.getReference().getName().equals("eSuperTypes") && isProxySuperTypeDifference(rc))) {
								registerChange(d.getMatch(), d);
							}
						}
					}
				}
				else if (d instanceof ResourceAttachmentChange) {
					// change at the root of the metamodel
					otherDiffsCounter += 1;
					otherDiffs.add(d);
					countFeatureDiff(d);
				}
				break;

			case MOVE:
				if (d instanceof ReferenceChange) {
					ReferenceChange rc = (ReferenceChange) d;
					if (rc.getReference().isContainment()) {
						if (isCutoffType(d)) {
							registerChange(d.getMatch(), d);
						}
						else if (isSubordinateType(d)) {
							Match m = getFirstNotSubordinateParent(d);
							if (m != null) {
								registerChange(m, d);
							}
						}
						else {
							otherDiffsCounter += 1; // alternative way of counting because the matched elements are the containers
							otherDiffs.add(d);
							countFeatureDiff(d);
						}
					}
					else {
						System.out.println("THIS SHOULD NOT HAPPEN: " + rc.getReference());
					}
				}
			}
		}

		for (Match m : changesMap.keySet()) {
			countChangeDiff(m);
		}
		numberOfAffectedElements = changesMap.size() + otherDiffsCounter;
	}

	protected Match getFirstNotSubordinateParent(Diff d) {
		Match m = d.getMatch();
		while (m != null && isSubordinateType(m)) {
			m = (Match) m.eContainer();
		}
		return m;
	}

	protected boolean existLeftAndRight(Match match) {
		return match.getLeft() != null && match.getRight() != null;
	}

	protected boolean isAnnotationRelated(Diff d) {
		if (d instanceof ReferenceChange) {
			ReferenceChange rc = (ReferenceChange) d;
			if (rc.getReference().getName().equals("eAnnotations")) {
				return true;
			}
		}
		return false;
	}

	protected boolean isGenericsRelated(Diff d) {
		if (d instanceof ReferenceChange) {
			ReferenceChange rc = (ReferenceChange) d;
			if (rc.getReference().getName().equals("eGenericSuperTypes") ||
					rc.getReference().getName().equals("eGenericType") ||
					rc.getReference().getName().equals("eTypeParameters")) {
				return true;
			}
		}
		return false;
	}

	protected boolean isSubordinateType(Diff d) {
		if (useAllTypes) {
			return false;
		}
		else if (isAnnotationRelated(d)) {
			return false;
		}
		if (isGenericsRelated(d)) {
			return true;
		}
		return isSubordinateType(d.getMatch());
	}

	protected boolean isSubordinateType(Match m) {

		switch (getAffectedType(m).getName()) {
			case "EParameter":
			case "EStringToStringMapEntry":
			case "EGenericType":
			case "ETypeParameter":
				return true;
			default:
				return false;
		}
	}

	/**
	 * A cutoff type marks where we should stop checking (because anything
	 * below is a subordinate type)
	 */
	protected boolean isCutoffType(Diff d) {
		if (useAllTypes) {
			return false;
		}
		else if (isAnnotationRelated(d)) {
			return false;
		}
		switch (getAffectedType(d).getName()) {
			case "EOperation":
			case "EAnnotation":
				return true;
			default:
				return false;
		}
	}

	protected void registerChange(Match m, Diff d) {
		List<Diff> diffs = changesMap.getOrDefault(m, new ArrayList<>());
		diffs.add(d);
		changesMap.putIfAbsent(m, diffs);
	}

	protected void countChangeDiff(Match m) {
		String key = "CHANGE-";
		if (m.getLeft() != null) {
			key += m.getLeft().eClass().getName();
		}
		else if (m.getRight() != null) {
			key += m.getRight().eClass().getName();
		}
		diffCounts.put(key, diffCounts.getOrDefault(key, 0) + 1);
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

		if (leftType == null || rightType == null) {
			return false;
		}
		return leftType.eIsProxy() != rightType.eIsProxy();
	}

	protected void countFeatureDiff(Diff d) {
		String key = d.getKind().getLiteral();
		if (d instanceof ReferenceChange) {
			ReferenceChange rc = (ReferenceChange) d;
			key += "-" + rc.getValue().eClass().getName();

			if (d.getKind() == DifferenceKind.CHANGE) {
				key += "SHOULDNOTHAPPEN";
			}
		}
		else if (d instanceof AttributeChange) {
			AttributeChange ac = (AttributeChange) d;
			key += "-" + getAffectedType(d).getName();
			if (d.getKind() != DifferenceKind.CHANGE) {
				key += "." + ac.getAttribute().getName();
			}
		}
		else if (d instanceof ResourceAttachmentChange) {
			ResourceAttachmentChange rac = (ResourceAttachmentChange) d;
			Match m = rac.getMatch();
			key += "-ResourceAttachment" + ".";
			if (d.getKind() == DifferenceKind.ADD) {
				key += m.getLeft().eClass().getName();
			}
			else if (d.getKind() == DifferenceKind.DELETE) {
				key += m.getRight().eClass().getName();
			}
		}
		diffCounts.put(key, diffCounts.getOrDefault(key, 0) + 1);
	}

	protected EClass getAffectedType(Diff d) {
		return getAffectedType(d.getMatch());
	}

	protected EClass getAffectedType(Match m) {
		if (m.getLeft() != null) {
			return m.getLeft().eClass();
		}
		else {
			return m.getRight().eClass();
		}
	}

	public int getNumberOfDifferences() {
		return numberOfDifferences;
	}

	public Comparison getComparison() {
		return comparison;
	}

	public int countAllElements(Resource resource) {
		int count = 0;

		// Use EcoreUtil to get all contents in the resource
		Iterator<EObject> allContents = EcoreUtil.getAllContents(resource.getContents(), false);

		while (allContents.hasNext()) {
			allContents.next();
			count++; // Increment for each element
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

	public String getLeftPath() {
		return leftPath;
	}

	public String getRightPath() {
		return rightPath;
	}

	public Map<Match, List<Diff>> getChangesMap() {
		return changesMap;
	}

	public List<Diff> getOtherDiffs() {
		return otherDiffs;
	}

	/**
	 * Disable cutoff and subordinate types
	 */
	public void setUseAllTypes(boolean useAllTypes) {
		this.useAllTypes = useAllTypes;
	}
}
