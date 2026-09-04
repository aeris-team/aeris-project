import {
  SquaresFour,
  VideoCamera,
  Crosshair,
  MapTrifold,
  X,
  List,
  BatteryFull,
  Drone,
  CellSignalFull,
  CloudSun,
  Bell,
  User,
  CaretDown,
  Gear,
  SignOut,
  Broadcast,
  NavigationArrow,
  Person,
  CornersOut,
  WarningCircle,
  CheckCircle,
  Check,
  ArrowRight,
  Info,
  MapPin,
} from '@phosphor-icons/react';

type IconName =
  | 'squares-four'
  | 'video-camera'
  | 'crosshair'
  | 'map-trifold'
  | 'x'
  | 'list'
  | 'battery-full'
  | 'drone'
  | 'cell-signal-full'
  | 'cloud-sun'
  | 'bell'
  | 'user'
  | 'caret-down'
  | 'gear'
  | 'sign-out'
  | 'broadcast'
  | 'navigation-arrow'
  | 'person'
  | 'corners-out'
  | 'warning-circle'
  | 'check-circle'
  | 'check'
  | 'arrow-right'
  | 'info'
  | 'map-pin';

const iconMap: Record<IconName, any> = {
  'squares-four': SquaresFour,
  'video-camera': VideoCamera,
  'crosshair': Crosshair,
  'map-trifold': MapTrifold,
  'x': X,
  'list': List,
  'battery-full': BatteryFull,
  'drone': Drone,
  'cell-signal-full': CellSignalFull,
  'cloud-sun': CloudSun,
  'bell': Bell,
  'user': User,
  'caret-down': CaretDown,
  'gear': Gear,
  'sign-out': SignOut,
  'broadcast': Broadcast,
  'navigation-arrow': NavigationArrow,
  'person': Person,
  'corners-out': CornersOut,
  'warning-circle': WarningCircle,
  'check-circle': CheckCircle,
  'check': Check,
  'arrow-right': ArrowRight,
  'info': Info,
  'map-pin': MapPin,
};

interface IconProps {
  name: IconName;
  weight?: 'thin' | 'light' | 'regular' | 'bold' | 'fill' | 'duotone';
  className?: string;
  size?: number | string;
}

export function Icon({ name, weight = 'regular', className = '', size }: IconProps) {
  const Component = iconMap[name];
  if (!Component) return null;
  return <Component weight={weight} className={className} size={size} />;
}

export function IconFill({ name, className = '', size }: Omit<IconProps, 'weight'>) {
  return <Icon name={name} weight="fill" className={className} size={size} />;
}
