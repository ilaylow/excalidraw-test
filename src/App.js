import React, { useEffect, useState } from "react";
import { Excalidraw, convertToExcalidrawElements } from "@excalidraw/excalidraw";

const defaultElements = [
  {
    type: "rectangle",
    x: 100,
    y: 250,
    roundness: {
      type: 3
    },
  },
  {
    type: "ellipse",
    x: 250,
    y: 250,
  },
  {
    type: "diamond",
    x: 380,
    y: 250,
  },
]

function App() {
  const [elements, setElements] = useState(null);

  useEffect(() => {
    fetch('/excalidraw_elements.json')
      .then(res => res.json())
      .then(data => {
        console.log('Loaded data:', data);
        setElements(convertToExcalidrawElements(data));
      })
      .catch(err => {
        console.error('Error loading data:', err);
      });
  }, []);

  if (!elements) {
    return <div>Loading...</div>;  // Or null to show nothing
  }

  return (
    <div style={{ height: "710px" }}>
      <Excalidraw
        initialData={{
          elements,
          scrollToContent: true,
        }}
      />
    </div>
  );
}

export default App;
