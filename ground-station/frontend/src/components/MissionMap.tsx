import { useEffect, useRef, useState } from 'react';
import L from 'leaflet';
import { useAppStore } from '../stores/appStore';

type MapType = 'streets' | 'satellite';

const mapLayers: Record<MapType, { url: string; attribution: string }> = {
  streets: {
    url: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
    attribution: '&copy; OpenStreetMap contributors',
  },
  satellite: {
    url: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
    attribution: '&copy; Esri',
  },
};

export function MissionMap() {
  const { uav, survivor, home, setModalOpen, alertAcknowledged, hasRealGps } = useAppStore();
  const mapRef = useRef<HTMLDivElement>(null);
  const mapInstance = useRef<L.Map | null>(null);
  const tileLayer = useRef<L.TileLayer | null>(null);
  const uavMarker = useRef<L.Marker | null>(null);
  const survivorMarker = useRef<L.Marker | null>(null);
  const homeMarker = useRef<L.Marker | null>(null);
  const initialized = useRef(false);
  const flewToGps = useRef(false);
  const [mapType, setMapType] = useState<MapType>('streets');
  const [mapOffline, setMapOffline] = useState(() => !navigator.onLine);

  useEffect(() => {
    const goOnline = () => setMapOffline(false);
    const goOffline = () => setMapOffline(true);
    window.addEventListener('online', goOnline);
    window.addEventListener('offline', goOffline);
    return () => {
      window.removeEventListener('online', goOnline);
      window.removeEventListener('offline', goOffline);
    };
  }, []);

  useEffect(() => {
    if (!mapRef.current || initialized.current) return;

    const map = L.map(mapRef.current, {
      zoomControl: false,
    }).setView([uav.lat, uav.lng], 16);

    const addTiles = (type: MapType) => {
      const layer = L.tileLayer(mapLayers[type].url, {
        attribution: mapLayers[type].attribution,
      });
      layer.on('tileerror', () => setMapOffline(true));
      layer.on('tileload', () => setMapOffline(false));
      layer.addTo(map);
      tileLayer.current = layer;
    };

    addTiles('streets');

    const homeIcon = L.divIcon({
      className: 'custom-leaflet-marker',
      html: '<div class="w-6 h-6 bg-aeris rounded-full border-2 border-white flex items-center justify-center text-white font-bold text-[10px] shadow-md z-10">H</div>',
      iconSize: [24, 24],
      iconAnchor: [12, 12],
    });
    homeMarker.current = L.marker([home.lat, home.lng], { icon: homeIcon }).addTo(map);

    const survivorIcon = L.divIcon({
      className: 'custom-leaflet-marker',
      html: '<button class="cursor-pointer focus:outline-none rounded-full"><div class="absolute inset-0 rounded-full bg-danger opacity-40 animate-ping"></div><div class="relative w-6 h-6 bg-danger rounded-full border-2 border-white flex items-center justify-center text-white shadow-md"><i class="ph-fill ph-person text-sm"></i></div></button>',
      iconSize: [24, 24],
      iconAnchor: [12, 12],
    });
    survivorMarker.current = L.marker([survivor.lat, survivor.lng], { icon: survivorIcon }).addTo(map);
    survivorMarker.current.on('click', () => setModalOpen(true));

    const uavIcon = L.divIcon({
      className: 'custom-leaflet-marker',
      html: `<div class="w-6 h-6 bg-white rounded-full border-2 border-aeris flex items-center justify-center text-aeris shadow-md" style="transform: rotate(${uav.heading}deg)"><i class="ph-fill ph-navigation-arrow text-sm"></i></div>`,
      iconSize: [24, 24],
      iconAnchor: [12, 12],
    });
    uavMarker.current = L.marker([uav.lat, uav.lng], { icon: uavIcon }).addTo(map);

    mapInstance.current = map;
    initialized.current = true;
  }, []);

  useEffect(() => {
    if (tileLayer.current && mapInstance.current) {
      tileLayer.current.remove();
      const layer = L.tileLayer(mapLayers[mapType].url, {
        attribution: mapLayers[mapType].attribution,
      });
      layer.on('tileerror', () => setMapOffline(true));
      layer.on('tileload', () => setMapOffline(false));
      layer.addTo(mapInstance.current);
      tileLayer.current = layer;
    }
  }, [mapType]);

  useEffect(() => {
    if (homeMarker.current) homeMarker.current.setLatLng([home.lat, home.lng]);
    if (survivorMarker.current) survivorMarker.current.setLatLng([survivor.lat, survivor.lng]);
  }, [home.lat, home.lng, survivor.lat, survivor.lng]);

  useEffect(() => {
    if (!hasRealGps || flewToGps.current || !mapInstance.current) return;
    flewToGps.current = true;
    mapInstance.current.flyTo([home.lat, home.lng], 16, { duration: 1.2 });
  }, [hasRealGps, home.lat, home.lng]);

  useEffect(() => {
    if (uavMarker.current) {
      uavMarker.current.setLatLng([uav.lat, uav.lng]);
      const el = uavMarker.current.getElement();
      const arrow = el?.querySelector('div') as HTMLElement | null;
      if (arrow) {
        const dx = survivor.lng - uav.lng;
        const dy = survivor.lat - uav.lat;
        const targetBearing = 90 - Math.atan2(dy, dx) * (180 / Math.PI);
        
        const currentTransform = arrow.style.transform;
        const match = currentTransform.match(/rotate\(([-\d.]+)deg\)/);
        let currentBearing = match ? parseFloat(match[1]) : 0;
        
        let diff = targetBearing - currentBearing;
        while (diff > 180) diff -= 360;
        while (diff < -180) diff += 360;
        
        currentBearing = currentBearing + diff * 0.05;
        currentBearing = currentBearing % 360;
        
        arrow.style.transform = `rotate(${currentBearing}deg)`;
      }
    }
  }, [uav.lat, uav.lng, survivor.lat, survivor.lng]);

  useEffect(() => {
    if (survivorMarker.current && alertAcknowledged) {
      const el = survivorMarker.current.getElement();
      const ping = el?.querySelector('.animate-ping');
      if (ping) ping.remove();
    }
  }, [alertAcknowledged]);

  const mapTypes: { id: MapType; label: string }[] = [
    { id: 'streets', label: 'Streets' },
    { id: 'satellite', label: 'Satellite' },
  ];

  return (
    <div className="lg:col-span-5 panel-card p-0 relative min-h-[300px] lg:min-h-0">
      <div className="absolute top-4 left-4 z-10 bg-white/90 backdrop-blur-sm px-3 py-1.5 rounded-md shadow-sm border border-slate-200 flex items-center gap-2">
        <h2 className="text-sm font-bold text-slate-800">MISSION MAP</h2>
        <div className="flex items-center gap-1 ml-2 bg-slate-100 rounded-md p-0.5">
          {mapTypes.map((type) => (
            <button
              key={type.id}
              onClick={() => setMapType(type.id)}
              className={`px-2 py-0.5 text-[9px] font-medium rounded transition-colors ${
                mapType === type.id
                  ? 'bg-white text-slate-800 shadow-sm'
                  : 'text-slate-500 hover:text-slate-700'
              }`}
            >
              {type.label}
            </button>
          ))}
        </div>
      </div>

      <div ref={mapRef} className="absolute inset-0 z-0 rounded-xl overflow-hidden" />

      {mapOffline && (
        <div className="absolute top-4 right-4 z-10 bg-amber-500 text-white text-[10px] font-bold uppercase tracking-wider px-2.5 py-1 rounded shadow-sm">
          Offline — markers only
        </div>
      )}

      <div className="hidden sm:flex absolute bottom-4 right-4 bg-white/90 backdrop-blur-sm p-3 rounded-lg border border-slate-200 shadow-sm text-[10px] text-slate-600 flex-col gap-2 z-10 pointer-events-none">
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 rounded-full bg-aeris text-white flex items-center justify-center text-[8px]">H</div>
          Home (Base)
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 rounded-full border-2 border-aeris flex items-center justify-center text-aeris">
            <i className="ph-fill ph-navigation-arrow text-[10px]" />
          </div>
          UAV Position
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 rounded-full bg-danger flex items-center justify-center text-white">
            <i className="ph-fill ph-person text-[10px]" />
          </div>
          Survivor Detected
        </div>
      </div>
    </div>
  );
}
