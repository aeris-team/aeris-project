import { useEffect } from 'react';
import { useAppStore } from '../stores/appStore';

export function useGeolocation() {
  const setRealGpsLocation = useAppStore((s) => s.setRealGpsLocation);

  useEffect(() => {
    if (!navigator.geolocation) return;

    const watchId = navigator.geolocation.watchPosition(
      (pos) => {
        setRealGpsLocation(pos.coords.latitude, pos.coords.longitude);
      },
      () => {
        // permission denied / unavailable — keep defaults, app still works offline
      },
      {
        enableHighAccuracy: true,
        timeout: 15000,
        maximumAge: 10000,
      }
    );

    return () => navigator.geolocation.clearWatch(watchId);
  }, [setRealGpsLocation]);
}
