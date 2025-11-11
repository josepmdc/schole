import { useEffect, useMemo, useRef, useState, type Dispatch, type SetStateAction } from "react";
import * as d3 from "d3";

const MARGIN = { top: 30, right: 75, bottom: 80, left: 100 };
const BUBBLE_MIN_SIZE = 4;
const BUBBLE_MAX_SIZE = 40;

export interface Point {
  id: string;
  x: number;
  y: number;
  size: number;
}

interface Targets {
  lowerBound: number | null;
  upperBound: number | null;
}

interface BubblePlotProps {
  width: number;
  height: number;
  data: Point[];
  setData: Dispatch<SetStateAction<Point[]>>;
  targets: Targets;
}

interface Domain {
  x: [number, number];
  y: [number, number];
}

export const BubblePlot = ({ width, height, data, setData, targets }: BubblePlotProps) => {
  const axesRef = useRef<SVGGElement>(null);
  const bubblesRef = useRef<SVGGElement>(null);
  const rangeLinesRef = useRef<SVGGElement>(null);

  const boundsWidth = width - MARGIN.left - MARGIN.right;
  const boundsHeight = height - MARGIN.top - MARGIN.bottom;

  const [initialDomain, setInitialDomain] = useState<Domain | null>(null);

  useEffect(() => {
    if (data.length && !initialDomain) {
      let xVals = data.map((d) => d.x);
      let yVals = data.map((d) => d.y);

      // push target bounds to make sure the solution is in the graph. Add 10 to offer wiggle room
      if (targets.lowerBound) {
        yVals.push(targets.lowerBound + 10);
      }
      if (targets.upperBound) {
        yVals.push(targets.upperBound - 10);
      }

      const xExtent = d3.extent(xVals) as [number, number];
      const yExtent = d3.extent(yVals) as [number, number];
      setInitialDomain({ x: xExtent, y: yExtent });
    }
  }, [data, initialDomain]);

  const xScale = useMemo(() => {
    const domain = initialDomain?.x ?? (d3.extent(data.map((d) => d.x)) as [number, number]);
    return d3.scaleLinear().domain(domain).range([0, boundsWidth]).nice();
  }, [initialDomain, boundsWidth]);

  const yScale = useMemo(() => {
    const domain = initialDomain?.y ?? (d3.extent(data.map((d) => d.y)) as [number, number]);
    return d3.scaleLinear().domain(domain).range([boundsHeight, 0]).nice();
  }, [initialDomain, boundsHeight]);

  const sizeScale = useMemo(() => {
    const [min, max] = d3.extent(data.map((d) => d.size)) as [number, number];
    return d3.scaleSqrt().domain([min, max]).range([BUBBLE_MIN_SIZE, BUBBLE_MAX_SIZE]);
  }, [data]);

  // render graph
  useEffect(() => {
    if (!axesRef.current) return;

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

  // render min max lines
  useEffect(() => {
    if (!rangeLinesRef.current || data.length == 0) return;

    const yValues = data.map((p) => p.y);

    const [min, max] = [Math.min(...yValues), Math.max(...yValues)];

    const svgElement = d3.select(rangeLinesRef.current);
    svgElement.selectAll("*").remove();

    const maxColor = "#3da1e3";

    svgElement
      .append("line")
      .attr("stroke", maxColor)
      .attr("stroke-width", 2)
      .attr("x1", 0)
      .attr("y1", yScale(max))
      .attr("x2", boundsWidth)
      .attr("y2", yScale(max));

    svgElement
      .append("text")
      .attr("x", boundsWidth + 10)
      .attr("y", yScale(max) + 4)
      .attr("font-size", 12)
      .attr("fill", maxColor)
      .text(`MAX (${Math.round(max)})`);

    const minColor = "#e3743d";

    svgElement
      .append("line")
      .attr("stroke", minColor)
      .attr("stroke-width", 2)
      .attr("x1", 0)
      .attr("y1", yScale(min))
      .attr("x2", boundsWidth)
      .attr("y2", yScale(min));

    svgElement
      .append("text")
      .attr("x", boundsWidth + 10)
      .attr("y", yScale(min) + 4)
      .attr("font-size", 12)
      .attr("fill", minColor)
      .text(`MIN (${Math.round(min)})`);
  }, [data, rangeLinesRef, yScale, width]);

  // Drag behavior
  useEffect(() => {
    if (!bubblesRef.current) return;

    const getWithinBounds = (limit: number, value: number) => Math.max(0, Math.min(limit, value));

    const drag = d3.drag<SVGCircleElement, string>().on("drag", function (e, draggedPointId) {
      // Keep within bounds
      const newX = getWithinBounds(boundsWidth, e.x);
      const newY = getWithinBounds(boundsHeight, e.y);

      // Update circle position
      d3.select(this).attr("cx", newX).attr("cy", newY);

      // we need to invert the coordinates again since our data is in cartesian coordinates
      const newData = { x: xScale.invert(newX), y: yScale.invert(newY) };

      // update data with new coordinates
      setData((currentPoints) =>
        currentPoints.map((p) => (p.id === draggedPointId ? { ...p, ...newData } : p)),
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
        <g ref={axesRef} transform={`translate(${MARGIN.left},${MARGIN.top})`} />
        <g ref={rangeLinesRef} transform={`translate(${MARGIN.left},${MARGIN.top})`} />
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
      </svg>
    </>
  );
};
