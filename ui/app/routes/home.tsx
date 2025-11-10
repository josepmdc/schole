import { BubblePlot } from "~/components/graph";
import type { Route } from "./+types/home";
import { useState } from "react";

export function meta({ }: Route.MetaArgs) {
    return [
        { title: "Scholé" },
        { name: "description", content: "Welcome to Scholé!" },
    ];
}

export default function Home() {
    const [points, setPoints] = useState(data);

    return (
        <div className="flex h-screen m-5">
            <div className="max-w-full lg:max-w-1/2 m-auto rounded-lg shadow flex flex-col">
                <div className="flex flex-col lg:flex-row">
                    <div className="m-10 lg:w-1/3 flex flex-col">
                        <div className="grow">
                            <h1>Exercise 1</h1>
                            <p>Move around the data point to make the range be between 200 and 500</p>
                        </div>
                        <div className="flex justify-center">
                            <button className="p-2 m-2 rounded-lg bg-amber-100">Next Exercise</button>
                        </div>
                    </div>
                    <BubblePlot data={points} setData={setPoints} width={500} height={400} />
                </div>
            </div>
        </div>
    );
}


export const data = [
    {
        "id": 1,
        "x": 974.5803384,
        "y": 43.828,
        "size": 123,
    },
    {
        "id": 2,
        "x": 5937.029526,
        "y": 76.423,
        "size": 321,
    },
    {
        "id": 3,
        "x": 6223.367465,
        "y": 72.301,
        "size": 223,
    },
    {
        "id": 4,
        "x": 4797.231267,
        "y": 42.731,
        "size": 532,
    },
    {
        "id": 5,
        "x": 12779.37964,
        "y": 75.32,
        "size": 210,
    },
    {
        "id": 6,
        "x": 34435.36744,
        "y": 81.235,
        "size": 321,
    },
    {
        "id": 7,
        "x": 36126.4927,
        "y": 79.829,
        "size": 419,
    },
]
