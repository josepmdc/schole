import { useEffect, useMemo, useRef, useState, type Dispatch, type SetStateAction } from "react";
import * as d3 from "d3";

const MARGIN = { top: 30, right: 30, bottom: 80, left: 100 };
const BUBBLE_MIN_SIZE = 4;
const BUBBLE_MAX_SIZE = 40;

export interface Point {
  id: string;
  x: number;
  y: number;
  size: number;
}

interface BubblePlotProps {
  width: number;
  height: number;
  data: Point[];
  setData: Dispatch<SetStateAction<Point[]>>;
}

export const BubblePlot = ({ width, height, data, setData }: BubblePlotProps) => {
  const axesRef = useRef<SVGGElement>(null);
  const bubblesRef = useRef<SVGGElement>(null);

  const boundsWidth = width - MARGIN.left - MARGIN.right;
  const boundsHeight = height - MARGIN.top - MARGIN.bottom;

  const xScale = useMemo(() => {
    const [min, max] = d3.extent(data.map((d) => d.x)) as [number, number];
    return d3.scaleLinear().domain([min, max]).range([0, boundsWidth]).nice();
  }, [data, boundsWidth]);

  const yScale = useMemo(() => {
    const [min, max] = d3.extent(data.map((d) => d.y)) as [number, number];
    return d3.scaleLinear().domain([min, max]).range([boundsHeight, 0]).nice();
  }, [data, boundsHeight]);

  const sizeScale = useMemo(() => {
    const [min, max] = d3.extent(data.map((d) => d.size)) as [number, number];
    return d3.scaleSqrt().domain([min, max]).range([BUBBLE_MIN_SIZE, BUBBLE_MAX_SIZE]);
  }, [data]);

  // render graph
  useEffect(() => {
    const svgElement = d3.select(axesRef.current);

    svgElement.selectAll("*").remove();

    svgElement
      .append("g")
      .attr("transform", `translate(0, ${boundsHeight})`)
      .call(d3.axisBottom(xScale));

    svgElement.append("g").call(d3.axisLeft(yScale));

    // X Axis Label
    svgElement
      .append("text")
      .attr("font-size", 14)
      .attr("text-anchor", "middle")
      .attr("x", boundsWidth / 2)
      .attr("y", boundsHeight + 40)
      .attr("fill", "#374151")
      .attr("font-weight", "bold")
      .text("Input Value (X)");

    // Y Axis Label
    svgElement
      .append("text")
      .attr("font-size", 14)
      .attr("text-anchor", "middle")
      .attr("x", -boundsHeight / 2)
      .attr("y", -50)
      .attr("fill", "#374151")
      .attr("font-weight", "bold")
      .attr("transform", "rotate(-90)")
      .text("Output Value (Y)");
  }, [xScale, yScale, boundsHeight, boundsWidth]);

  // Drag behavior
  useEffect(() => {
    if (!bubblesRef.current) return;

    const getWithinBounds = (limit: number, value: number) => Math.max(0, Math.min(limit, value));

    const drag = d3
      .drag<SVGCircleElement, string>()
      .on("drag", function (e) {
        // Keep within bounds
        const newX = getWithinBounds(boundsWidth, e.x);
        const newY = getWithinBounds(boundsHeight, e.y);

        // Update circle position
        d3.select(this).attr("cx", newX).attr("cy", newY);
      })
      .on("end", (e, draggedPointId) => {
        const x = xScale.invert(getWithinBounds(boundsWidth, e.x));
        const y = yScale.invert(getWithinBounds(boundsHeight, e.y));

        setData((currentPoints) =>
          currentPoints.map((p) => (p.id === draggedPointId ? { ...p, x: x, y: y } : p)),
        );
      });

    d3.select(bubblesRef.current)
      .selectAll("circle")
      .data(data.map((p) => p.id))
      .call(drag as any);
  }, [data, xScale, yScale, boundsWidth, boundsHeight]);

  return (
    <>
      <svg width="100%" viewBox={`0 0 ${width} ${height}`}>
        <g ref={bubblesRef} transform={`translate(${MARGIN.left},${MARGIN.top})`}>
          {data
            .sort((a, b) => b.size - a.size)
            .map((point, i) => (
              <circle
                key={i}
                r={sizeScale(point.size)}
                cx={xScale(point.x)}
                cy={yScale(point.y)}
                fill="#69b3a2"
                stroke="#333"
                fillOpacity={0.6}
                strokeWidth={1}
              />
            ))}
        </g>

        <g ref={axesRef} transform={`translate(${MARGIN.left},${MARGIN.top})`} />
      </svg>
    </>
  );
};
