// dashboard/src/components/CountryMap.tsx
import {
  ComposableMap,
  Geographies,
  Geography,
  Marker,
} from "react-simple-maps"
import type { Attack } from "../types/Attack"

const geoUrl =
  "https://cdn.jsdelivr.net/npm/world-atlas@2/countries-110m.json"

export default function CountryMap({ attacks }: { attacks: Attack[] }) {
  // Filter attacks with valid coordinates
  const validAttacks = attacks
    .filter(
      (a) =>
        a.latitude != null &&
        a.longitude != null &&
        a.country_code !== "XX"
    )
    .slice(0, 200)

  return (
    <div className="w-full h-96 bg-gray-900 rounded-lg overflow-hidden">
      <ComposableMap projectionConfig={{ scale: 145, center: [0, 20] }}>
        <Geographies geography={geoUrl}>
          {({ geographies }: { geographies: any[] }) =>
            geographies.map((geo) => (
              <Geography
                key={geo.rsmKey}
                geography={geo}
                fill="#111827"
                stroke="#374151"
                style={{
                  default: { outline: "none" },
                  hover: { outline: "none" },
                  pressed: { outline: "none" },
                }}
              />
            ))
          }
        </Geographies>

        {validAttacks.length === 0 ? (
          <text
            x="50%"
            y="50%"
            textAnchor="middle"
            fill="#666"
            className="text-lg font-medium"
          >
            Waiting for attacks...
          </text>
        ) : (
          validAttacks.map((attack, i) => (
            <Marker
              key={attack.id || i}
              coordinates={[Number(attack.longitude), Number(attack.latitude)]}
            >
              <circle
                cx={0}
                cy={0}
                r={6}
                fill="#ef4444"
                opacity={0.9}
                stroke="#991b1b"
                strokeWidth={2}
              >
                <animate
                  attributeName="r"
                  values="4;9;4"
                  dur="2s"
                  repeatCount="indefinite"
                />
                <animate
                  attributeName="opacity"
                  values="1;0.4;1"
                  dur="2s"
                  repeatCount="indefinite"
                />
              </circle>
            </Marker>
          ))
        )}
      </ComposableMap>
    </div>
  )
}