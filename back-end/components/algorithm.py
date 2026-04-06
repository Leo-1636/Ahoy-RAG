PIXEL_GAP = 1.0
EXCLUDED_TYPES = {"Page-header", "Page-footer"}

class BBox:
    @staticmethod
    def touch_bbox(bbox_a: list, bbox_b: list) -> bool:
        return bbox_a[0] < bbox_b[2] and bbox_a[2] > bbox_b[0] and bbox_a[1] < bbox_b[3] and bbox_a[3] > bbox_b[1]

    @staticmethod
    def union_bbox(bboxes: list) -> list:
        x_min = min(bbox[0] for bbox in bboxes)
        y_min = min(bbox[1] for bbox in bboxes)
        x_max = max(bbox[2] for bbox in bboxes)
        y_max = max(bbox[3] for bbox in bboxes)
        best_bbox = max(bboxes, key = lambda b: b[4])
        return [x_min, y_min, x_max, y_max, best_bbox[4], best_bbox[5]]
    
class ReadingOrderAlgorithm:
    def __init__(self, results: list, classes: list[str]):
        self.elements = []
        for result in sorted(results, key = lambda result: result[1]):
            *bbox, class_id = result
            label = classes[class_id]
            if label not in EXCLUDED_TYPES:
                self.elements.append([*bbox, label])

        self.union_elements()
        self.reading_order = self.global_grouping(self.elements) if self.elements else []
    
    def union_elements(self):
        merged_elements = []
        for element in self.elements:
            for merged_element in merged_elements:
                if BBox.touch_bbox(element, merged_element):
                    merged_element[:] = BBox.union_bbox([element, merged_element])
                    break
            else:
                merged_elements.append(element)
        self.elements = merged_elements

    def global_grouping(self, elements: list) -> list:
        x_groups = self.group_by_gap(elements, 0)
        if len(x_groups) > 1:
            return [element for group in x_groups for element in self.local_grouping(group)]
        y_groups = self.group_by_gap(elements, 1)
        if len(y_groups) > 1:
            return [element for group in y_groups for element in self.global_grouping(group)]
        return sorted(elements, key = lambda element: (element[1], element[0]))

    def local_grouping(self, elements: list) -> list:
        for axis in (1, 0):
            groups = self.group_by_gap(elements, axis)
            if len(groups) > 1:
                return [element for group in groups for element in self.local_grouping(group)]
        return sorted(elements, key = lambda element: (element[1], element[0]))

    def group_by_gap(self, elements: list, axis: int) -> list[float]:
        axis_intervals = sorted(
            ((element[axis], element[axis + 2]) for element in elements),
            key = lambda interval: interval[0],
        )
        cut_points = []
        axis_point = axis_intervals[0][1]
        for start_pixel, end_pixel in axis_intervals[1:]:
            if start_pixel - axis_point >= PIXEL_GAP:
                cut_points.append((axis_point + start_pixel) / 2)
            axis_point = max(axis_point, end_pixel)
        
        if not cut_points:
            return [elements]

        groups = []
        interval_bounds = [float("-inf")] + cut_points + [float("inf")]
        for i in range(len(interval_bounds) - 1):
            group_range = interval_bounds[i], interval_bounds[i + 1]
            group = [
                element for element in elements
                if group_range[0] <= (element[axis] + element[axis + 2]) / 2 < group_range[1]
            ]
            if group:
                groups.append(group)
        return groups