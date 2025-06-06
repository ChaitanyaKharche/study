import React, { useEffect, useRef, memo } from 'react';
import CytoscapeComponent from 'react-cytoscapejs';
import cytoscape from 'cytoscape';
import coseBilkent from 'cytoscape-cose-bilkent';
import dagre from 'cytoscape-dagre';

cytoscape.use(coseBilkent);
cytoscape.use(dagre);

// Define layoutOptions outside the component as it's static
const staticLayoutOptions = {
  name: 'cose-bilkent',
  animate: 'end',
  animationEasing: 'ease-out',
  animationDuration: 1000,
  randomize: true,
  idealEdgeLength: 150,
  nodeRepulsion: 10000,
};

// const staticLayoutDagre = { // Dagre is good for hierarchical/directed graphs
//   name: 'dagre',
//   rankDir: 'TB', // Top to bottom
//   spacingFactor: 1.25
// };

const MindMapDisplay = memo(({ mindMapData, docId }) => {
  const cyRef = useRef(null);

  const elements = CytoscapeComponent.normalizeElements(mindMapData);

  useEffect(() => {
    if (cyRef.current) {
      const cy = cyRef.current;
      cy.elements().remove();
      cy.add(elements);    
      
      // Use the staticLayoutOptions defined outside
      const layout = cy.layout(staticLayoutOptions); 
      layout.pon('layoutstop').then(() => {
         cy.animate({
            fit: { padding: 30 },
            duration: 500 
        });
      });
      layout.run();

      cy.on('tap', 'node', (event) => {
        const node = event.target;
        console.log('Tapped node:', node.id(), node.data('label'), node.data('full_text'));
        // You can display node.data('full_text') in a modal or side panel here
      });

      // Cleanup: remove event listeners when component unmounts or mindMapData changes
      return () => {
        if (cyRef.current) {
            cyRef.current.removeListener('tap', 'node');
            // Or more generally: cyRef.current.removeAllListeners(); if appropriate
        }
      };
    }
  // Now useEffect only depends on things that actually change based on props/state
  }, [mindMapData, elements, docId]); // layoutOptions removed from here

  return (
    <CytoscapeComponent
      elements={elements}
      style={{ width: '100%', height: '500px', border: '1px solid #ccc' }}
      layout={staticLayoutOptions} // Initial layout
      cy={(cy) => { cyRef.current = cy; }}
      stylesheet={[
        {
          selector: 'node',
          style: {
            'background-color': '#66a3ff',
            'label': 'data(label)',
            'width': 'label',
            'height': 'label',
            'padding': '10px',
            'shape': 'round-rectangle',
            'text-valign': 'center',
            'text-halign': 'center',
            'font-size': '10px',
            'text-wrap': 'wrap',
            'text-max-width': '100px',
            'border-width': 1,
            'border-color': '#4d88ff'
          }
        },
        {
          selector: 'edge',
          style: {
            'width': 2,
            'line-color': '#ccc',
            'target-arrow-color': '#ccc',
            'target-arrow-shape': 'triangle',
            'curve-style': 'bezier'
          }
        }
      ]}
    />
  );
});

export default MindMapDisplay;