import { MapContainer, TileLayer, CircleMarker, Polyline, Tooltip } from 'react-leaflet';
import { CLUSTER_COLORS } from '../data';

const TILE_URL = 'https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png';

function popRadius(pop) {
  return Math.max(3, Math.min(14, Math.sqrt(pop / 500000) * 4));
}

export default function MapView({ scenario }) {
  return (
    <MapContainer
      center={[38.5, -96]}
      zoom={4}
      style={{ height: '100%', width: '100%' }}
      zoomControl={true}
    >
      <TileLayer url={TILE_URL} />

      {scenario.warehouses.flatMap((cluster, ci) => {
        const color = CLUSTER_COLORS[ci % CLUSTER_COLORS.length];
        const fac = cluster.facility;
        const elements = [];

        // Lines: demand node -> warehouse
        cluster.demand_nodes.forEach((node, ni) => {
          elements.push(
            <Polyline
              key={`line-${ci}-${ni}`}
              positions={[[node.lat, node.lng], [fac.lat, fac.lng]]}
              pathOptions={{ color, weight: 1, opacity: 0.45 }}
            />
          );
        });

        // Demand node circles
        cluster.demand_nodes.forEach((node, ni) => {
          elements.push(
            <CircleMarker
              key={`node-${ci}-${ni}`}
              center={[node.lat, node.lng]}
              radius={popRadius(node.population)}
              pathOptions={{ color, fillColor: color, fillOpacity: 0.65, weight: 1 }}
            >
              <Tooltip direction="top" offset={[0, -4]}>
                <span className="font-semibold">{node.city}, {node.state_id}</span>
                <br />
                Pop: {(node.population / 1e6).toFixed(2)}M
                <br />
                {node.distance_to_facility_mi} mi to warehouse
              </Tooltip>
            </CircleMarker>
          );
        });

        // Warehouse marker (larger, white border)
        elements.push(
          <CircleMarker
            key={`wh-${ci}`}
            center={[fac.lat, fac.lng]}
            radius={13}
            pathOptions={{ color: '#0f172a', fillColor: color, fillOpacity: 1, weight: 2.5 }}
          >
            <Tooltip permanent direction="top" offset={[0, -16]}>
              <strong>{fac.city}, {fac.state_id}</strong>
            </Tooltip>
          </CircleMarker>
        );

        return elements;
      })}
    </MapContainer>
  );
}
