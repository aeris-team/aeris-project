export interface UAVTelemetry {
  altitude: number;
  speed: number;
  heading: number;
  battery: number;
  lat: number;
  lng: number;
}

export interface LinkHealth {
  latency: number;
  rssi: number;
  bitrate?: number;
  plr?: number;
}

export interface CommLinks {
  wifi: LinkHealth;
  lora: LinkHealth;
}

export interface SurvivorDetection {
  id: string;
  timestamp: string;
  confidence: number;
  lat: number;
  lng: number;
  altitude: number;
  distance: number;
  status: 'new' | 'acknowledged';
  imageUrl?: string;
  thermalImageUrl?: string;
}

export interface Mission {
  id: string;
  name: string;
  startedAt: string;
  endedAt?: string;
  status: 'active' | 'ended';
}

export interface DetectionPacket {
  timestamp: string;
  confidence: number;
  lat: number;
  lng: number;
  altitude: number;
  distance: number;
  frameNumber: number;
}
