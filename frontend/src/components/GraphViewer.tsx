import React, { useEffect, useRef } from 'react';
import CytoscapeComponent from 'react-cytoscapejs';
import cytoscape from 'cytoscape';
import { GraphViewerProps, GraphData } from '../types';

const GraphViewer: React.FC<GraphViewerProps> = ({ 
  data,
  onNodeClick,
  onEdgeClick 
}) => {
  const cyRef = useRef<cytoscape.Core | null>(null);

  const cytoscapeStylesheet: cytoscape.Stylesheet[] = [
    {
      selector: 'node',
      style: {
        'background-color': 'data(color)',
        'label': 'data(label)',
        'width': 'data(size)',
        'height': 'data(size)',
        'font-size': '10px',
        'text-valign': 'bottom',
        'text-halign': 'center'
      }
    },
    {
      selector: 'edge',
      style: {
        'width': 'mapData(weight, 0, 100, 1, 5)',
        'line-color': '#ccc',
        'target-arrow-color': '#ccc',
        'target-arrow-shape': 'triangle',
        'curve-style': 'bezier'
      }
    }
  ];

  const formatGraphData = (graphData: GraphData) => ({
    nodes: graphData.nodes.map(node => ({
      data: {
        id: node.id,
        label: node.label,
        size: node.size,
        color: node.color,
        ...node.properties
      }
    })),
    edges: graphData.edges.map(edge => ({
      data: {
        id: `${edge.source}-${edge.target}`,
        source: edge.source,
        target: edge.target,
        weight: edge.weight,
        ...edge.properties
      }
    }))
  });

  return (
    <div className="cytoscape-container">
      <CytoscapeComponent
        elements={formatGraphData(data)}
        stylesheet={cytoscapeStylesheet}
        style={{
          width: '100%',
          height: '100%'
        }}
        cy={(cy) => {
          cyRef.current = cy;
          cy.on('tap', 'node', (evt) => onNodeClick?.(evt.target.id()));
          cy.on('tap', 'edge', (evt) => {
            const edge = evt.target;
            onEdgeClick?.({
              source: edge.source().id(),
              target: edge.target().id(),
              weight: edge.data('weight'),
              properties: edge.data('properties')
            });
          });
          cy.layout({ name: 'cose', animate: true }).run();
        }}
      />
    </div>
  );
};

export default GraphViewer;