"use client";

import dynamic from "next/dynamic";
import type { Data, Layout } from "plotly.js";
import type { PositionPoint } from "@/lib/research-result";

const Plot = dynamic(() => import("react-plotly.js"), { ssr: false });

type Props = {
  points: PositionPoint[];
  selectedFixtureId?: string;
  onSelect: (fixtureId: string) => void;
};

export function ResearchChart({ points, selectedFixtureId, onSelect }: Props) {
  const data: Data[] = [
    {
      x: points.map((point) => point.date),
      y: points.map((point) => point.position),
      customdata: points.map((point) => point.fixtureId),
      type: "scatter",
      mode: "lines+markers",
      line: { color: "#e85d3f", width: 3 },
      marker: {
        color: points.map((point) => point.fixtureId === selectedFixtureId ? "#9aaa42" : "#e85d3f"),
        size: points.map((point) => point.fixtureId === selectedFixtureId ? 11 : 8),
        line: { color: "#fffdf8", width: 2 },
      },
      hovertemplate: "%{x}<br>%{text}<br>Position %{y}<extra></extra>",
      text: points.map((point) => point.opponent),
    },
  ];

  const layout: Partial<Layout> = {
    margin: { l: 48, r: 18, t: 18, b: 44 },
    paper_bgcolor: "rgba(0,0,0,0)",
    plot_bgcolor: "rgba(0,0,0,0)",
    font: { family: "inherit", color: "#171714" },
    xaxis: {
      showgrid: false,
      zeroline: false,
      linecolor: "rgba(24,23,20,0.11)",
    },
    yaxis: {
      title: { text: "League position" },
      autorange: "reversed",
      dtick: 1,
      gridcolor: "rgba(24,23,20,0.08)",
      zeroline: false,
    },
    hoverlabel: { bgcolor: "#fffdf8", font: { color: "#171714" } },
    dragmode: "zoom",
  };

  return (
    <Plot
      data={data}
      layout={layout}
      config={{ responsive: true, displaylogo: false, modeBarButtonsToRemove: ["lasso2d", "select2d"] }}
      useResizeHandler
      style={{ width: "100%", height: "420px" }}
      onClick={(event) => {
        const point = event.points?.[0];
        const fixtureId = point?.customdata;
        if (fixtureId) onSelect(String(fixtureId));
      }}
    />
  );
}
