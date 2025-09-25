
# member3_tracker.py
from collections import OrderedDict
import numpy as np

class CentroidTracker:
    def __init__(self, max_disappeared=30, max_distance=50): 

        self.nextObjectID = 0
        self.objects = OrderedDict()
        self.bboxes = OrderedDict()
        self.disappeared = OrderedDict()
        self.max_disappeared = max_disappeared
        self.max_distance = max_distance

    def update(self, rects):
        if len(rects) == 0:
            for oid in list(self.disappeared.keys()):
                self.disappeared[oid] += 1
                if self.disappeared[oid] > self.max_disappeared:
                    self._deregister(oid)
            return self.bboxes

        input_centroids = np.zeros((len(rects), 2), dtype="int")
        for i, (x1,y1,x2,y2) in enumerate(rects):
            input_centroids[i] = (int((x1+x2)/2), int((y1+y2)/2))

        if len(self.objects) == 0:
            for i in range(len(input_centroids)):
                self._register(input_centroids[i], rects[i])
        else:
            objectIDs = list(self.objects.keys())
            objectCentroids = list(self.objects.values())
            D = np.linalg.norm(np.array(objectCentroids)[:, None] - input_centroids[None, :], axis=2)
            rows = D.min(axis=1).argsort()
            cols = D.argmin(axis=1)[rows]
            usedRows, usedCols = set(), set()

            for row, col in zip(rows, cols):
                if row in usedRows or col in usedCols: continue
                if D[row, col] > self.max_distance: continue
                oid = objectIDs[row]
                self.objects[oid] = input_centroids[col]
                self.bboxes[oid] = rects[col]
                self.disappeared[oid] = 0
                usedRows.add(row)
                usedCols.add(col)

            unusedCols = set(range(D.shape[1])) - usedCols
            for col in unusedCols:
                self._register(input_centroids[col], rects[col])
            unusedRows = set(range(D.shape[0])) - usedRows
            for row in unusedRows:
                oid = objectIDs[row]
                self.disappeared[oid] += 1
                if self.disappeared[oid] > self.max_disappeared:
                    self._deregister(oid)
        return self.bboxes

    def _register(self, centroid, bbox):
        self.objects[self.nextObjectID] = centroid
        self.bboxes[self.nextObjectID] = bbox
        self.disappeared[self.nextObjectID] = 0
        self.nextObjectID += 1

    def _deregister(self, oid):
        del self.objects[oid]
        del self.bboxes[oid]
        del self.disappeared[oid]