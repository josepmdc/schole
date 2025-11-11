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

      // push target bounds to make sure the solution is in the graph
      if (targets.lowerBound) {
        yVals.push(targets.lowerBound);
      }
      if (targets.upperBound) {
        yVals.push(targets.upperBound);
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

  useEffect(() => {
    if (!rangeLinesRef.current || data.length == 0) return;

    const yValues = data.map((p) => p.y);
    console.log(yValues);
    const [min, max] = [Math.min(...yValues), Math.max(...yValues)];
    console.log(min, max);

    const svgElement = d3.select(rangeLinesRef.current);
    svgElement.selectAll("*").remove();

    svgElement
      .append("line")
      .attr("stroke", "#3da1e3")
      .attr("stroke-width", 2)
      .attr("x1", 0)
      .attr("y1", yScale(max))
      .attr("x2", boundsWidth)
      .attr("y2", yScale(max));

    svgElement
      .append("line")
      .attr("stroke", "#e3743d")
      .attr("stroke-width", 2)
      .attr("x1", 0)
      .attr("y1", yScale(min))
      .attr("x2", boundsWidth)
      .attr("y2", yScale(min));
  }, [data, rangeLinesRef, yScale, width]);

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
