#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
3D 空間資料模型
基於 Google Earth 的資料結構
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
import json

class GeometryType(Enum):
    """幾何類型"""
    POINT = "Point"
    LINESTRING = "LineString"
    POLYGON = "Polygon"
    MULTIPOINT = "MultiPoint"
    MULTILINESTRING = "MultiLineString"
    MULTIPOLYGON = "MultiPolygon"
    MODEL = "Model"

class CoordinateSystem(Enum):
    """座標系統"""
    WGS84 = "WGS84"
    ECEF = "ECEF"
    UTM = "UTM"

@dataclass
class Coordinate3D:
    """3D 座標"""
    longitude: float
    latitude: float
    altitude: float = 0.0
    coordinate_system: CoordinateSystem = CoordinateSystem.WGS84
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "longitude": self.longitude,
            "latitude": self.latitude,
            "altitude": self.altitude,
            "coordinate_system": self.coordinate_system.value
        }
    
    def to_geojson(self) -> List[float]:
        return [self.longitude, self.latitude, self.altitude]

@dataclass
class Geometry3D:
    """3D 幾何物件"""
    type: GeometryType
    coordinates: List[Any]
    properties: Dict[str, Any] = field(default_factory=dict)
    
    def to_geojson(self) -> Dict[str, Any]:
        return {
            "type": self.type.value,
            "coordinates": self.coordinates
        }
    
    def to_kml(self) -> str:
        if self.type == GeometryType.POINT:
            coord = self.coordinates[0]
            return f"<Point><coordinates>{coord[0]},{coord[1]},{coord[2] if len(coord) > 2 else 0}</coordinates></Point>"
        elif self.type == GeometryType.POLYGON:
            coords_str = " ".join([f"{c[0]},{c[1]},{c[2] if len(c) > 2 else 0}" for c in self.coordinates[0]])
            return f"<Polygon><outerBoundaryIs><LinearRing><coordinates>{coords_str}</coordinates></LinearRing></outerBoundaryIs></Polygon>"
        elif self.type == GeometryType.LINESTRING:
            coords_str = " ".join([f"{c[0]},{c[1]},{c[2] if len(c) > 2 else 0}" for c in self.coordinates])
            return f"<LineString><coordinates>{coords_str}</coordinates></LineString>"
        return ""

@dataclass
class SpatialFeature:
    """空間特徵"""
    id: str
    name: str
    description: Optional[str] = None
    geometry: Optional[Geometry3D] = None
    style: Dict[str, Any] = field(default_factory=dict)
    time_span: Optional[Dict[str, datetime]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def to_geojson(self) -> Dict[str, Any]:
        return {
            "type": "Feature",
            "id": self.id,
            "properties": {
                "name": self.name,
                "description": self.description,
                "style": self.style,
                "metadata": self.metadata,
                "created_at": self.created_at.isoformat(),
                "updated_at": self.updated_at.isoformat()
            },
            "geometry": self.geometry.to_geojson() if self.geometry else None
        }
    
    def to_kml_placemark(self) -> str:
        kml = f"""<Placemark>
    <name>{self.name}</name>
    <description>{self.description or ''}</description>
    {self.geometry.to_kml() if self.geometry else ''}
</Placemark>"""
        return kml

@dataclass
class SpatialLayer:
    """空間圖層"""
    id: str
    name: str
    description: Optional[str] = None
    features: List[SpatialFeature] = field(default_factory=list)
    visible: bool = True
    opacity: float = 1.0
    style: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_feature(self, feature: SpatialFeature):
        self.features.append(feature)
    
    def to_geojson(self) -> Dict[str, Any]:
        return {
            "type": "FeatureCollection",
            "properties": {
                "name": self.name,
                "description": self.description,
                "visible": self.visible,
                "opacity": self.opacity
            },
            "features": [f.to_geojson() for f in self.features]
        }
    
    def to_kml_folder(self) -> str:
        features_kml = "\n".join([f.to_kml_placemark() for f in self.features])
        return f"""<Folder>
    <name>{self.name}</name>
    <description>{self.description or ''}</description>
    {features_kml}
</Folder>"""

@dataclass
class SpatialDataset:
    """空間資料集"""
    id: str
    name: str
    description: Optional[str] = None
    layers: List[SpatialLayer] = field(default_factory=list)
    coordinate_system: CoordinateSystem = CoordinateSystem.WGS84
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def add_layer(self, layer: SpatialLayer):
        self.layers.append(layer)
    
    def to_geojson(self) -> Dict[str, Any]:
        all_features = []
        for layer in self.layers:
            if layer.visible:
                all_features.extend([f.to_geojson() for f in layer.features])
        
        return {
            "type": "FeatureCollection",
            "properties": {
                "name": self.name,
                "description": self.description,
                "coordinate_system": self.coordinate_system.value
            },
            "features": all_features
        }
    
    def to_kml(self) -> str:
        layers_kml = "\n".join([l.to_kml_folder() for l in self.layers if l.visible])
        return f"""<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
    <Document>
        <name>{self.name}</name>
        <description>{self.description or ''}</description>
        {layers_kml}
    </Document>
</kml>"""
    
    def save_kml(self, filepath: str):
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(self.to_kml())
    
    def save_geojson(self, filepath: str):
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.to_geojson(), f, indent=2, ensure_ascii=False)

class SpatialQuery:
    """空間查詢類"""
    
    @staticmethod
    def distance_haversine(coord1: Coordinate3D, coord2: Coordinate3D) -> float:
        """計算兩點間距離（Haversine 公式，單位：米）"""
        from math import radians, sin, cos, sqrt, atan2
        
        R = 6371000  # 地球半徑（米）
        
        lat1, lon1 = radians(coord1.latitude), radians(coord1.longitude)
        lat2, lon2 = radians(coord2.latitude), radians(coord2.longitude)
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        
        distance = R * c
        altitude_diff = abs(coord1.altitude - coord2.altitude)
        total_distance = sqrt(distance**2 + altitude_diff**2)
        
        return total_distance
