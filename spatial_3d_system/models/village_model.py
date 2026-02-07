#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
里別 3D 空間模型
五常里、五順里、仁忠里的詳細 3D 空間邏輯
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime
import json

from .spatial_data import (
    SpatialFeature, SpatialLayer, SpatialDataset,
    Geometry3D, GeometryType, Coordinate3D,
    SpatialQuery
)


@dataclass
class VillageBoundary:
    """里別邊界"""
    village_id: str
    village_name: str
    coordinates: List[Coordinate3D]  # 邊界座標點
    area_m2: float = 0.0  # 面積（平方米）
    perimeter_m: float = 0.0  # 周長（米）
    center: Optional[Coordinate3D] = None  # 中心點
    
    def calculate_center(self) -> Coordinate3D:
        """計算中心點"""
        if not self.coordinates:
            return None
        
        lons = [c.longitude for c in self.coordinates]
        lats = [c.latitude for c in self.coordinates]
        
        return Coordinate3D(
            longitude=sum(lons) / len(lons),
            latitude=sum(lats) / len(lats),
            altitude=sum(c.altitude for c in self.coordinates) / len(self.coordinates)
        )
    
    def to_geometry(self) -> Geometry3D:
        """轉換為幾何物件"""
        coords = [[c.longitude, c.latitude, c.altitude] for c in self.coordinates]
        # 閉合多邊形
        coords.append(coords[0])
        
        return Geometry3D(
            type=GeometryType.POLYGON,
            coordinates=[coords]
        )


@dataclass
class Road:
    """道路"""
    road_id: str
    name: str
    road_type: str  # 'major', 'secondary', 'alley'
    coordinates: List[Coordinate3D]  # 道路中心線座標
    width_m: float = 0.0  # 道路寬度（米）
    description: str = ""
    
    def to_geometry(self) -> Geometry3D:
        """轉換為幾何物件（線段）"""
        coords = [[c.longitude, c.latitude, c.altitude] for c in self.coordinates]
        
        return Geometry3D(
            type=GeometryType.LINESTRING,
            coordinates=coords
        )


@dataclass
class Building:
    """建築物"""
    building_id: str
    name: str
    building_type: str  # 'residential', 'commercial', 'public'
    footprint: List[Coordinate3D]  # 建築物基底座標
    height_m: float = 0.0  # 建築物高度（米）
    floors: int = 0  # 樓層數
    description: str = ""
    
    def to_geometry(self) -> Geometry3D:
        """轉換為幾何物件（3D 多邊形）"""
        coords = [[c.longitude, c.latitude, c.altitude] for c in self.footprint]
        coords.append(coords[0])  # 閉合
        
        return Geometry3D(
            type=GeometryType.POLYGON,
            coordinates=[coords]
        )
    
    def to_3d_model(self) -> Dict:
        """轉換為 3D 模型資料"""
        return {
            "id": self.building_id,
            "name": self.name,
            "type": self.building_type,
            "footprint": [[c.longitude, c.latitude, c.altitude] for c in self.footprint],
            "height": self.height_m,
            "floors": self.floors,
            "extruded_height": self.height_m
        }


@dataclass
class Village3D:
    """里別 3D 空間模型"""
    village_id: str
    village_name: str
    village_name_en: str
    boundary: VillageBoundary
    roads: List[Road] = field(default_factory=list)
    buildings: List[Building] = field(default_factory=list)
    facilities: List[SpatialFeature] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_road(self, road: Road):
        """添加道路"""
        self.roads.append(road)
    
    def add_building(self, building: Building):
        """添加建築物"""
        self.buildings.append(building)
    
    def add_facility(self, facility: SpatialFeature):
        """添加設施"""
        self.facilities.append(facility)
    
    def to_spatial_dataset(self) -> SpatialDataset:
        """轉換為空間資料集"""
        dataset = SpatialDataset(
            id=f"village_{self.village_id}",
            name=f"{self.village_name} 3D 空間資料",
            description=f"{self.village_name}的詳細 3D 空間模型"
        )
        
        # 邊界圖層
        boundary_layer = SpatialLayer(
            id=f"{self.village_id}_boundary",
            name=f"{self.village_name}邊界",
            description=f"{self.village_name}行政邊界"
        )
        
        boundary_feature = SpatialFeature(
            id=f"{self.village_id}_boundary",
            name=f"{self.village_name}邊界",
            description=f"{self.village_name}行政區域邊界",
            geometry=self.boundary.to_geometry(),
            style={"color": "#4CAF50", "opacity": 0.3, "outline": True, "outlineColor": "#4CAF50"}
        )
        boundary_layer.add_feature(boundary_feature)
        dataset.add_layer(boundary_layer)
        
        # 道路圖層
        if self.roads:
            roads_layer = SpatialLayer(
                id=f"{self.village_id}_roads",
                name=f"{self.village_name}道路",
                description=f"{self.village_name}道路網路"
            )
            
            for road in self.roads:
                road_feature = SpatialFeature(
                    id=road.road_id,
                    name=road.name,
                    description=road.description,
                    geometry=road.to_geometry(),
                    style={
                        "color": "#FF9800" if road.road_type == "major" else "#FFC107",
                        "width": road.width_m,
                        "roadType": road.road_type
                    }
                )
                roads_layer.add_feature(road_feature)
            
            dataset.add_layer(roads_layer)
        
        # 建築物圖層
        if self.buildings:
            buildings_layer = SpatialLayer(
                id=f"{self.village_id}_buildings",
                name=f"{self.village_name}建築物",
                description=f"{self.village_name}建築物 3D 模型"
            )
            
            for building in self.buildings:
                building_feature = SpatialFeature(
                    id=building.building_id,
                    name=building.name,
                    description=building.description,
                    geometry=building.to_geometry(),
                    style={
                        "color": "#9E9E9E",
                        "height": building.height_m,
                        "floors": building.floors,
                        "buildingType": building.building_type
                    },
                    metadata=building.to_3d_model()
                )
                buildings_layer.add_feature(building_feature)
            
            dataset.add_layer(buildings_layer)
        
        # 設施圖層
        if self.facilities:
            facilities_layer = SpatialLayer(
                id=f"{self.village_id}_facilities",
                name=f"{self.village_name}設施",
                description=f"{self.village_name}公共設施"
            )
            
            for facility in self.facilities:
                facilities_layer.add_feature(facility)
            
            dataset.add_layer(facilities_layer)
        
        return dataset
    
    def to_kml(self) -> str:
        """轉換為 KML 格式"""
        dataset = self.to_spatial_dataset()
        return dataset.to_kml()
    
    def to_geojson(self) -> Dict:
        """轉換為 GeoJSON 格式"""
        dataset = self.to_spatial_dataset()
        return dataset.to_geojson()


# 三個里的預設資料
def create_wuchang_li() -> Village3D:
    """建立五常里 3D 模型"""
    # 五常里邊界（約略，需要實際 GIS 資料精確化）
    boundary_coords = [
        Coordinate3D(121.4850, 25.0780, 0),  # 西南
        Coordinate3D(121.4950, 25.0780, 0),  # 東南
        Coordinate3D(121.4950, 25.0850, 0),  # 東北
        Coordinate3D(121.4850, 25.0850, 0),  # 西北
    ]
    
    boundary = VillageBoundary(
        village_id="wuchang_li",
        village_name="五常里",
        coordinates=boundary_coords
    )
    boundary.center = boundary.calculate_center()
    
    village = Village3D(
        village_id="wuchang_li",
        village_name="五常里",
        village_name_en="Wuchang Li",
        boundary=boundary,
        metadata={
            "population": 5249,
            "households": 2092,
            "area_type": "redevelopment_area",
            "description": "仁義重劃區主要區域"
        }
    )
    
    # 主要道路
    renyi_street = Road(
        road_id="renyi_street",
        name="仁義街",
        road_type="major",
        coordinates=[
            Coordinate3D(121.4860, 25.0790, 0),
            Coordinate3D(121.4940, 25.0830, 0)
        ],
        width_m=12.0,
        description="貫穿五常里的主要道路"
    )
    village.add_road(renyi_street)
    
    wuhua_street = Road(
        road_id="wuhua_street",
        name="五華街",
        road_type="major",
        coordinates=[
            Coordinate3D(121.4870, 25.0800, 0),
            Coordinate3D(121.4930, 25.0820, 0)
        ],
        width_m=10.0,
        description="商業大動脈"
    )
    village.add_road(wuhua_street)
    
    # 重要建築物/設施
    coffee_shop = Building(
        building_id="wuchang_coffee",
        name="上品聊國咖啡館",
        building_type="commercial",
        footprint=[
            Coordinate3D(121.4898, 25.0818, 0),
            Coordinate3D(121.4900, 25.0818, 0),
            Coordinate3D(121.4900, 25.0820, 0),
            Coordinate3D(121.4898, 25.0820, 0)
        ],
        height_m=10.0,
        floors=2,
        description="五常社區核心商家"
    )
    village.add_building(coffee_shop)
    
    return village


def create_wushun_li() -> Village3D:
    """建立五順里 3D 模型"""
    boundary_coords = [
        Coordinate3D(121.4820, 25.0720, 0),
        Coordinate3D(121.4920, 25.0720, 0),
        Coordinate3D(121.4920, 25.0780, 0),
        Coordinate3D(121.4820, 25.0780, 0),
    ]
    
    boundary = VillageBoundary(
        village_id="wushun_li",
        village_name="五順里",
        coordinates=boundary_coords
    )
    boundary.center = boundary.calculate_center()
    
    village = Village3D(
        village_id="wushun_li",
        village_name="五順里",
        village_name_en="Wushun Li",
        boundary=boundary,
        metadata={
            "population": 4021,
            "households": 1520,
            "area_type": "traditional_commercial",
            "description": "傳統商業區"
        }
    )
    
    # 道路
    wuhua_street = Road(
        road_id="wuhua_street_wushun",
        name="五華街",
        road_type="major",
        coordinates=[
            Coordinate3D(121.4830, 25.0730, 0),
            Coordinate3D(121.4910, 25.0770, 0)
        ],
        width_m=10.0
    )
    village.add_road(wuhua_street)
    
    return village


def create_renzhong_li() -> Village3D:
    """建立仁忠里 3D 模型"""
    boundary_coords = [
        Coordinate3D(121.4750, 25.0670, 0),
        Coordinate3D(121.4850, 25.0670, 0),
        Coordinate3D(121.4850, 25.0730, 0),
        Coordinate3D(121.4750, 25.0730, 0),
    ]
    
    boundary = VillageBoundary(
        village_id="renzhong_li",
        village_name="仁忠里",
        coordinates=boundary_coords
    )
    boundary.center = boundary.calculate_center()
    
    village = Village3D(
        village_id="renzhong_li",
        village_name="仁忠里",
        village_name_en="Renzhong Li",
        boundary=boundary,
        metadata={
            "population": 3254,
            "households": 1279,
            "area_type": "traditional_residential",
            "description": "傳統住宅區"
        }
    )
    
    # 道路
    renai_street = Road(
        road_id="renai_street",
        name="仁愛街",
        road_type="secondary",
        coordinates=[
            Coordinate3D(121.4760, 25.0680, 0),
            Coordinate3D(121.4840, 25.0720, 0)
        ],
        width_m=8.0
    )
    village.add_road(renai_street)
    
    return village


# 範例使用
if __name__ == "__main__":
    # 建立三個里的模型
    wuchang = create_wuchang_li()
    wushun = create_wushun_li()
    renzhong = create_renzhong_li()
    
    # 輸出為 KML
    print("=== 五常里 KML ===")
    print(wuchang.to_kml()[:500])
    
    # 輸出為 GeoJSON
    print("\n=== 五常里 GeoJSON ===")
    print(json.dumps(wuchang.to_geojson(), indent=2, ensure_ascii=False)[:500])
    
    print(f"\n五常里: {len(wuchang.roads)} 條道路, {len(wuchang.buildings)} 棟建築物")
    print(f"五順里: {len(wushun.roads)} 條道路, {len(wushun.buildings)} 棟建築物")
    print(f"仁忠里: {len(renzhong.roads)} 條道路, {len(renzhong.buildings)} 棟建築物")
