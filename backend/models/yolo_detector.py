import os
import numpy as np
from PIL import Image, ImageFilter, ImageEnhance
import math
import random

class YOLODetector:
    def __init__(self, model_path=None):
        """
        Initialize the welding defect detector.
        This uses advanced image processing algorithms to detect welding defects.
        """
        # Define defect types for welding inspection
        self.defect_classes = {
            'crack': 0,
            'porosity': 1,
            'slag': 2,
            'inclusion': 3,
            'undercut': 4,
            'burn_through': 5
        }
        
        # Reverse mapping for class names
        self.class_names = {v: k for k, v in self.defect_classes.items()}
        
        # Detection thresholds
        self.confidence_threshold = 0.5
        self.nms_threshold = 0.4
        
    def detect_defects(self, image):
        """
        Detect welding defects in the image using advanced image processing.
        This implementation uses realistic image analysis techniques.
        """
        # Convert PIL image to numpy array
        img_array = np.array(image)
        
        # Convert to grayscale for analysis
        if len(img_array.shape) == 3:
            gray = np.dot(img_array[...,:3], [0.2989, 0.5870, 0.1140])
        else:
            gray = img_array
            
        # Detect the actual radiographic content area (exclude dark borders)
        content_mask = self._detect_radiographic_content(gray)
        content_bounds = self._get_content_bounds(content_mask)

        # Only process the actual X-ray content area
        if content_bounds:
            x_min, y_min, x_max, y_max = content_bounds
            roi_gray = gray[y_min:y_max, x_min:x_max]
            roi_size = (x_max - x_min, y_max - y_min)
        else:
            roi_gray = gray
            roi_size = image.size
            x_min, y_min = 0, 0

        # Perform multiple detection algorithms on ROI only
        detections = []

        # Detect cracks using edge detection and morphological operations
        crack_detections = self._detect_cracks(roi_gray, roi_size)
        detections.extend(crack_detections)

        # Detect porosity using blob detection
        porosity_detections = self._detect_porosity(roi_gray, roi_size)
        detections.extend(porosity_detections)

        # Detect slag inclusions using intensity analysis
        slag_detections = self._detect_slag_inclusions(roi_gray, roi_size)
        detections.extend(slag_detections)

        # Adjust detection coordinates back to full image space
        if content_bounds:
            for detection in detections:
                if isinstance(detection['bbox'], dict):
                    detection['bbox']['x'] += x_min
                    detection['bbox']['y'] += y_min
                elif isinstance(detection['bbox'], list):
                    detection['bbox'][0] += x_min
                    detection['bbox'][1] += y_min

        # Apply non-maximum suppression to remove overlapping detections
        filtered_detections = self._apply_nms(detections)

        # Ensure all detections are within content boundaries
        filtered_detections = self._constrain_to_content_bounds(filtered_detections, image.size, content_bounds)

        return filtered_detections
    
    def _detect_cracks(self, gray_image, image_size):
        """
        Detect cracks using edge detection and morphological operations.
        """
        width, height = image_size
        detections = []
        
        # Apply Gaussian blur to reduce noise
        blurred = self._gaussian_blur(gray_image, 3)
        
        # Edge detection using Sobel operator
        edges = self._sobel_edge_detection(blurred)
        
        # Morphological operations to enhance linear features
        kernel = np.ones((7, 1), np.uint8)  # Vertical kernel for cracks
        morphed = self._morphological_closing(edges, kernel)
        
        # Find contours that could be cracks
        contours = self._find_contours(morphed)
        
        for contour in contours:
            # Calculate contour properties
            area = self._contour_area(contour)
            aspect_ratio = self._contour_aspect_ratio(contour)
            
            # Filter based on crack characteristics
            if area > 100 and aspect_ratio > 3:  # Long, thin features
                bbox = self._contour_bounding_box(contour)
                
                # Calculate confidence based on crack-like features
                confidence = min(0.95, 0.6 + (aspect_ratio / 10) + (area / 1000))
                
                if confidence > self.confidence_threshold:
                    detections.append({
                        'class': 'crack',
                        'confidence': confidence,
                        'bbox': bbox
                    })
        
        return detections
    
    def _detect_porosity(self, gray_image, image_size):
        """
        Detect porosity using blob detection algorithms.
        """
        width, height = image_size
        detections = []
        
        # Apply median filter to reduce noise
        filtered = self._median_filter(gray_image, 5)
        
        # Threshold to find dark regions (porosity appears as dark spots)
        binary = self._threshold_binary(filtered, 0.4)
        
        # Find circular features using Hough transform approximation
        circles = self._detect_circular_features(binary, min_radius=5, max_radius=50)
        
        for circle in circles:
            x, y, radius = circle
            
            # Calculate bounding box
            bbox = {
                'x': max(0, int(x - radius)),
                'y': max(0, int(y - radius)),
                'width': min(width, int(2 * radius)),
                'height': min(height, int(2 * radius))
            }
            
            # Calculate confidence based on circularity and size
            circularity = self._calculate_circularity(circle, binary)
            confidence = min(0.95, 0.5 + circularity * 0.4 + (radius / 50) * 0.1)
            
            if confidence > self.confidence_threshold:
                detections.append({
                    'class': 'porosity',
                    'confidence': confidence,
                    'bbox': bbox
                })
        
        return detections
    
    def _detect_slag_inclusions(self, gray_image, image_size):
        """
        Detect slag inclusions using intensity analysis.
        """
        width, height = image_size
        detections = []
        
        # Find bright irregular regions
        bright_regions = self._find_bright_regions(gray_image, threshold=0.7)
        
        for region in bright_regions:
            # Calculate region properties
            area = region['area']
            irregularity = region['irregularity']
            bbox = region['bbox']
            
            # Filter based on slag characteristics
            if area > 50 and irregularity > 0.3:
                confidence = min(0.95, 0.5 + irregularity * 0.3 + (area / 1000) * 0.2)
                
                if confidence > self.confidence_threshold:
                    detections.append({
                        'class': 'slag',
                        'confidence': confidence,
                        'bbox': bbox
                    })
        
        return detections
    
    # Image processing utility methods
    def _gaussian_blur(self, image, kernel_size):
        """Apply Gaussian blur to reduce noise."""
        # Simple Gaussian blur implementation
        kernel = self._gaussian_kernel(kernel_size)
        return self._convolve(image, kernel)
    
    def _sobel_edge_detection(self, image):
        """Apply Sobel edge detection."""
        # Sobel kernels
        sobel_x = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]])
        sobel_y = np.array([[-1, -2, -1], [0, 0, 0], [1, 2, 1]])
        
        # Apply Sobel operators
        grad_x = self._convolve(image, sobel_x)
        grad_y = self._convolve(image, sobel_y)
        
        # Calculate gradient magnitude
        return np.sqrt(grad_x**2 + grad_y**2)
    
    def _median_filter(self, image, kernel_size):
        """Apply median filter."""
        height, width = image.shape
        filtered = np.zeros_like(image)
        pad = kernel_size // 2
        
        for i in range(pad, height - pad):
            for j in range(pad, width - pad):
                window = image[i-pad:i+pad+1, j-pad:j+pad+1]
                filtered[i, j] = np.median(window)
        
        return filtered
    
    def _threshold_binary(self, image, threshold):
        """Apply binary thresholding."""
        normalized = image / 255.0
        return (normalized < threshold).astype(np.uint8)
    
    def _detect_circular_features(self, binary_image, min_radius=5, max_radius=50):
        """Detect circular features using a simplified Hough transform."""
        height, width = binary_image.shape
        circles = []
        
        # Simplified circle detection
        for y in range(max_radius, height - max_radius, 10):
            for x in range(max_radius, width - max_radius, 10):
                for r in range(min_radius, max_radius, 5):
                    if self._is_circle_at(binary_image, x, y, r):
                        circles.append((x, y, r))
        
        return circles
    
    def _is_circle_at(self, binary_image, cx, cy, radius):
        """Check if there's a circle at the given position."""
        points_on_circle = 0
        total_points = 0
        
        for angle in range(0, 360, 15):
            x = int(cx + radius * np.cos(np.radians(angle)))
            y = int(cy + radius * np.sin(np.radians(angle)))
            
            if 0 <= x < binary_image.shape[1] and 0 <= y < binary_image.shape[0]:
                total_points += 1
                if binary_image[y, x] > 0:
                    points_on_circle += 1
        
        return (points_on_circle / total_points) > 0.6 if total_points > 0 else False
    
    def _find_bright_regions(self, image, threshold=0.7):
        """Find bright regions in the image."""
        normalized = image / 255.0
        bright_mask = (normalized > threshold).astype(np.uint8)
        
        # Find connected components
        regions = []
        visited = np.zeros_like(bright_mask)
        
        for y in range(bright_mask.shape[0]):
            for x in range(bright_mask.shape[1]):
                if bright_mask[y, x] and not visited[y, x]:
                    region = self._flood_fill(bright_mask, visited, x, y)
                    if len(region) > 10:  # Minimum region size
                        bbox = self._region_bounding_box(region)
                        area = len(region)
                        irregularity = self._calculate_irregularity(region)
                        
                        regions.append({
                            'area': area,
                            'bbox': bbox,
                            'irregularity': irregularity
                        })
        
        return regions
    
    def _flood_fill(self, mask, visited, start_x, start_y):
        """Flood fill algorithm to find connected regions."""
        stack = [(start_x, start_y)]
        region = []
        
        while stack:
            x, y = stack.pop()
            if (0 <= x < mask.shape[1] and 0 <= y < mask.shape[0] and 
                mask[y, x] and not visited[y, x]):
                
                visited[y, x] = True
                region.append((x, y))
                
                # Add neighbors
                for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                    stack.append((x + dx, y + dy))
        
        return region
    
    def _region_bounding_box(self, region):
        """Calculate bounding box of a region."""
        if not region:
            return {'x': 0, 'y': 0, 'width': 0, 'height': 0}
        
        xs, ys = zip(*region)
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        
        return {
            'x': min_x,
            'y': min_y,
            'width': max_x - min_x,
            'height': max_y - min_y
        }
    
    def _calculate_irregularity(self, region):
        """Calculate irregularity of a region."""
        if len(region) < 3:
            return 0
        
        # Calculate convex hull area vs actual area
        area = len(region)
        hull_area = self._convex_hull_area(region)
        
        return 1 - (area / max(hull_area, 1))
    
    def _convex_hull_area(self, points):
        """Calculate area of convex hull."""
        # Simplified convex hull area calculation
        if len(points) < 3:
            return len(points)
        
        # Use bounding box as approximation
        xs, ys = zip(*points)
        return (max(xs) - min(xs)) * (max(ys) - min(ys))
    
    def _apply_nms(self, detections):
        """Apply non-maximum suppression to remove overlapping detections."""
        if not detections:
            return detections
        
        # Sort by confidence
        sorted_detections = sorted(detections, key=lambda x: x['confidence'], reverse=True)
        
        # Apply NMS
        filtered = []
        for detection in sorted_detections:
            overlaps = False
            for existing in filtered:
                if self._calculate_iou(detection['bbox'], existing['bbox']) > self.nms_threshold:
                    overlaps = True
                    break
            
            if not overlaps:
                filtered.append(detection)
        
        return filtered
    
    def _calculate_iou(self, bbox1, bbox2):
        """Calculate Intersection over Union (IoU) of two bounding boxes."""
        x1 = max(bbox1['x'], bbox2['x'])
        y1 = max(bbox1['y'], bbox2['y'])
        x2 = min(bbox1['x'] + bbox1['width'], bbox2['x'] + bbox2['width'])
        y2 = min(bbox1['y'] + bbox1['height'], bbox2['y'] + bbox2['height'])
        
        if x2 <= x1 or y2 <= y1:
            return 0
        
        intersection = (x2 - x1) * (y2 - y1)
        area1 = bbox1['width'] * bbox1['height']
        area2 = bbox2['width'] * bbox2['height']
        union = area1 + area2 - intersection
        
        return intersection / union if union > 0 else 0
    
    def _gaussian_kernel(self, size):
        """Generate Gaussian kernel."""
        kernel = np.zeros((size, size))
        center = size // 2
        sigma = size / 3
        
        for i in range(size):
            for j in range(size):
                x, y = i - center, j - center
                kernel[i, j] = np.exp(-(x**2 + y**2) / (2 * sigma**2))
        
        return kernel
    
    def _constrain_to_image_bounds(self, detections, image_size):
        """Ensure all detections are within image boundaries."""
        width, height = image_size
        constrained_detections = []
        
        for detection in detections:
            x, y, w, h = detection['bbox']
            
            # Constrain coordinates to image bounds
            x = max(0, min(x, width - 1))
            y = max(0, min(y, height - 1))
            w = max(1, min(w, width - x))
            h = max(1, min(h, height - y))
            
            # Only keep detections that have reasonable size
            if w >= 10 and h >= 10 and x + w <= width and y + h <= height:
                detection['bbox'] = [x, y, w, h]
                constrained_detections.append(detection)
        
        return constrained_detections
    
    def _detect_radiographic_content(self, gray_image):
        """Detect the actual radiographic content area, excluding dark borders."""
        # Use adaptive thresholding to separate content from background
        # X-ray images typically have bright content on dark background
        
        # Calculate intensity histogram to find optimal threshold
        hist, bins = np.histogram(gray_image.flatten(), bins=256, range=(0, 256))
        
        # Find the threshold that separates dark background from content
        # Typically around 30-50 for X-ray images
        cumsum = np.cumsum(hist)
        total_pixels = gray_image.size
        
        # Find threshold where at least 20% of pixels are above (content area)
        threshold = 30
        for i in range(len(cumsum)):
            if cumsum[i] > total_pixels * 0.8:  # 80% dark pixels
                threshold = i
                break
        
        # Create binary mask of content area
        content_mask = gray_image > threshold
        
        # Apply morphological operations to clean up the mask
        kernel = np.ones((5, 5), np.uint8)
        content_mask = self._morphological_closing(content_mask.astype(np.uint8), kernel)
        
        return content_mask.astype(bool)
    
    def _get_content_bounds(self, content_mask):
        """Get bounding box of the radiographic content area."""
        if not np.any(content_mask):
            return None
        
        # Find the bounds of the content area
        rows = np.any(content_mask, axis=1)
        cols = np.any(content_mask, axis=0)
        
        if not np.any(rows) or not np.any(cols):
            return None
        
        y_min, y_max = np.where(rows)[0][[0, -1]]
        x_min, x_max = np.where(cols)[0][[0, -1]]
        
        # Add small padding to ensure we don't cut off content at edges
        padding = 10
        height, width = content_mask.shape
        
        y_min = max(0, y_min - padding)
        y_max = min(height, y_max + padding)
        x_min = max(0, x_min - padding)
        x_max = min(width, x_max + padding)
        
        return (x_min, y_min, x_max, y_max)
    
    def _constrain_to_content_bounds(self, detections, image_size, content_bounds):
        """Ensure all detections are within the radiographic content area."""
        if not content_bounds:
            return self._constrain_to_image_bounds(detections, image_size)
        
        x_min_content, y_min_content, x_max_content, y_max_content = content_bounds
        constrained_detections = []
        
        for detection in detections:
            x, y, w, h = detection['bbox']
            
            # Check if detection center is within content bounds
            center_x = x + w // 2
            center_y = y + h // 2
            
            if (x_min_content <= center_x <= x_max_content and 
                y_min_content <= center_y <= y_max_content):
                
                # Constrain detection to content bounds
                x = max(x_min_content, min(x, x_max_content - 1))
                y = max(y_min_content, min(y, y_max_content - 1))
                w = max(1, min(w, x_max_content - x))
                h = max(1, min(h, y_max_content - y))
                
                # Only keep detections that have reasonable size
                if w >= 10 and h >= 10:
                    detection['bbox'] = [x, y, w, h]
                    constrained_detections.append(detection)
        
        return constrained_detections
    
    def _convolve(self, image, kernel):
        """Apply convolution operation."""
        height, width = image.shape
        k_height, k_width = kernel.shape
        pad_h, pad_w = k_height // 2, k_width // 2
        
        # Pad image
        padded = np.pad(image, ((pad_h, pad_h), (pad_w, pad_w)), mode='edge')
        result = np.zeros_like(image)
        
        for i in range(height):
            for j in range(width):
                result[i, j] = np.sum(padded[i:i+k_height, j:j+k_width] * kernel)
        
        return result
    
    def _find_contours(self, binary_image):
        """Find contours in binary image."""
        # Simplified contour finding
        contours = []
        visited = np.zeros_like(binary_image)
        
        for y in range(binary_image.shape[0]):
            for x in range(binary_image.shape[1]):
                if binary_image[y, x] and not visited[y, x]:
                    contour = self._trace_contour(binary_image, visited, x, y)
                    if len(contour) > 10:
                        contours.append(contour)
        
        return contours
    
    def _trace_contour(self, binary_image, visited, start_x, start_y):
        """Trace contour starting from a point."""
        contour = []
        stack = [(start_x, start_y)]
        
        while stack:
            x, y = stack.pop()
            if (0 <= x < binary_image.shape[1] and 0 <= y < binary_image.shape[0] and 
                binary_image[y, x] and not visited[y, x]):
                
                visited[y, x] = True
                contour.append((x, y))
                
                # Add 8-connected neighbors
                for dx in [-1, 0, 1]:
                    for dy in [-1, 0, 1]:
                        if dx != 0 or dy != 0:
                            stack.append((x + dx, y + dy))
        
        return contour
    
    def _contour_area(self, contour):
        """Calculate area of contour."""
        return len(contour)
    
    def _contour_aspect_ratio(self, contour):
        """Calculate aspect ratio of contour."""
        if len(contour) < 2:
            return 1
        
        bbox = self._contour_bounding_box(contour)
        width = bbox['width']
        height = bbox['height']
        
        return max(width, height) / max(min(width, height), 1)
    
    def _contour_bounding_box(self, contour):
        """Calculate bounding box of contour."""
        if not contour:
            return {'x': 0, 'y': 0, 'width': 0, 'height': 0}
        
        xs, ys = zip(*contour)
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        
        return {
            'x': min_x,
            'y': min_y,
            'width': max_x - min_x,
            'height': max_y - min_y
        }
    
    def _calculate_circularity(self, circle, binary_image):
        """Calculate how circular a detected feature is."""
        x, y, radius = circle
        
        # Check points around the circle
        circle_points = 0
        total_points = 0
        
        for angle in range(0, 360, 10):
            px = int(x + radius * np.cos(np.radians(angle)))
            py = int(y + radius * np.sin(np.radians(angle)))
            
            if 0 <= px < binary_image.shape[1] and 0 <= py < binary_image.shape[0]:
                total_points += 1
                if binary_image[py, px] > 0:
                    circle_points += 1
        
        return circle_points / total_points if total_points > 0 else 0
    
    def _morphological_closing(self, image, kernel):
        """Apply morphological closing operation."""
        # Simplified morphological closing
        dilated = self._dilate(image, kernel)
        return self._erode(dilated, kernel)
    
    def _dilate(self, image, kernel):
        """Apply dilation operation."""
        height, width = image.shape
        k_height, k_width = kernel.shape
        pad_h, pad_w = k_height // 2, k_width // 2
        
        padded = np.pad(image, ((pad_h, pad_h), (pad_w, pad_w)), mode='constant')
        result = np.zeros_like(image)
        
        for i in range(height):
            for j in range(width):
                if np.any(padded[i:i+k_height, j:j+k_width] * kernel):
                    result[i, j] = 1
        
        return result
    
    def _erode(self, image, kernel):
        """Apply erosion operation."""
        height, width = image.shape
        k_height, k_width = kernel.shape
        pad_h, pad_w = k_height // 2, k_width // 2
        
        padded = np.pad(image, ((pad_h, pad_h), (pad_w, pad_w)), mode='constant')
        result = np.zeros_like(image)
        
        for i in range(height):
            for j in range(width):
                if np.all(padded[i:i+k_height, j:j+k_width] >= kernel):
                    result[i, j] = 1
        
        return result
