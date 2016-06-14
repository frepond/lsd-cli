import logging
import webbrowser
from tempfile import NamedTemporaryFile
import ujson as json

TEMPLATE = '''
<!DOCTYPE html>
<html>

<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>lsd vis</title>
    <style>
        @import url("http://fonts.googleapis.com/css?family=Open+Sans:300,400,600");
        svg {
            border: none;
        }

        .node {
            cursor: pointer;
        }

        .node text {
            font-size: 12px;
            font-family: 'Open Sans', 'Helvetica Neue', Helvetica, sans-serif;
            fill: #333333;
        }

        .d3-tip {
            font-size: 14px;
            font-family: 'Open Sans', 'Helvetica Neue', Helvetica, sans-serif;
            color: #333333;
            border: 1px solid #CCCCCC;
            border-radius: 5px;
            padding: 10px 20px;
            max-width: 250px;
            word-wrap: break-word;
            background-color: rgba(255, 255, 255, 0.9);
            text-align: left;
        }

        .link {
            fill: none;
            stroke: #DADFE1;
            stroke-width: 1px;
        }
    </style>
</head>

<body>
    <div class="container">
        <div id="graph"></div>
    </div>

    <script src="//cdn.jsdelivr.net/g/es6-promise@1.0.0"></script>
    <script src="//cdnjs.cloudflare.com/ajax/libs/jsonld/0.3.15/jsonld.js"></script>
    <script type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/d3/3.5.11/d3.min.js"></script>
    <script type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/d3-tip/0.6.7/d3-tip.min.js"></script>
    <script>
        (function() {
            'use strict';

            function jsonldVis(jsonld, selector, config) {
                if (!arguments.length) return jsonldVis;
                config = config || {};

                var h = config.h || 768,
                    w = config.w || 1024,
                    maxLabelWidth = config.maxLabelWidth || 250,
                    transitionDuration = config.transitionDuration || 750,
                    transitionEase = config.transitionEase || 'cubic-in-out',
                    minRadius = config.minRadius || 5,
                    scalingFactor = config.scalingFactor || 2;

                var i = 0;

                var tree = d3.layout.tree()
                    .size([h, w]);

                var diagonal = d3.svg.diagonal()
                    .projection(function(d) {
                        return [d.y, d.x];
                    });

                var svg = d3.select(selector).append('svg')
                    .attr('width', w)
                    .attr('height', h)
                    .append('g')
                    .attr('transform', 'translate(' + maxLabelWidth + ',0)');

                var tip = d3.tip()
                    .direction(function(d) {
                        return d.children || d._children ? 'w' : 'e';
                    })
                    .offset(function(d) {
                        return d.children || d._children ? [0, -3] : [0, 3];
                    })
                    .attr('class', 'd3-tip')
                    .html(function(d) {
                        return '<span>' + d.valueExtended + '</span>';
                    });

                svg.call(tip);

                var root = jsonldTree(jsonld);
                root.x0 = h / 2;
                root.y0 = 0;
                root.children.forEach(collapse);

                function changeSVGWidth(newWidth) {
                    if (w !== newWidth) {
                        d3.select(selector + ' > svg').attr('width', newWidth);
                    }
                }

                function jsonldTree(source) {
                    var tree = {};

                    if ('@id' in source) {
                        tree.isIdNode = true;
                        tree.name = source['@id'];
                        if (tree.name.length > maxLabelWidth / 9) {
                            tree.valueExtended = tree.name;
                            tree.name = '...' + \
                                tree.valueExtended.slice(
                                    -Math.floor(maxLabelWidth / 9));
                        }
                    } else {
                        tree.isIdNode = true;
                        tree.isBlankNode = true;
                        // random id, can replace with actual uuid generator if needed
                        tree.name = '_' + Math.random().toString(10).slice(-7);
                    }

                    var children = [];
                    Object.keys(source).forEach(function(key) {
                        if (key === '@id' || key === '@context' || source[key] === null) return;

                        var valueExtended, value;
                        if (typeof source[key] === 'object' && !Array.isArray(source[key])) {
                            children.push({
                                name: key,
                                children: [jsonldTree(source[key])]
                            });
                        } else if (Array.isArray(source[key])) {
                            children.push({
                                name: key,
                                children: source[key].map(function(item) {
                                    if (typeof item === 'object') {
                                        return jsonldTree(item);
                                    } else {
                                        return {
                                            name: item
                                        };
                                    }
                                })
                            });
                        } else {
                            valueExtended = source[key];
                            value = valueExtended;
                            if (value.length > maxLabelWidth / 9) {
                                value = value.slice(0, Math.floor(
                                    maxLabelWidth / 9)) + '...';
                                children.push({
                                    name: key,
                                    value: value,
                                    valueExtended: valueExtended
                                });
                            } else {
                                children.push({
                                    name: key,
                                    value: value
                                });
                            }
                        }
                    });

                    if (children.length) {
                        tree.children = children;
                    }

                    return tree;
                }

                function update(source) {
                    var nodes = tree.nodes(root).reverse();
                    var links = tree.links(nodes);

                    nodes.forEach(function(d) {
                        d.y = d.depth * maxLabelWidth;
                    });

                    var node = svg.selectAll('g.node')
                        .data(nodes, function(d) {
                            return d.id || (d.id = ++i);
                        });

                    var nodeEnter = node.enter()
                        .append('g')
                        .attr('class', 'node')
                        .attr('transform', function(d) {
                            return 'translate(' + source.y0 + ',' + source.x0 + ')';
                        })
                        .on('click', click);

                    nodeEnter.append('circle')
                        .attr('r', 0)
                        .style('stroke-width', function(d) {
                            return d.isIdNode ? '2px' : '1px';
                        })
                        .style('stroke', function(d) {
                            return d.isIdNode ? '#F7CA18' : '#4ECDC4';
                        })
                        .style('fill', function(d) {
                            if (d.isIdNode) {
                                return d._children ? '#F5D76E' : 'white';
                            } else {
                                return d._children ? '#86E2D5' : 'white';
                            }
                        })
                        .on('mouseover', function(d) {
                            if (d.valueExtended) tip.show(d);
                        })
                        .on('mouseout', tip.hide);

                    nodeEnter.append('text')
                        .attr('x', function(d) {
                            var spacing = computeRadius(d) + 5;
                            return d.children || d._children ? -spacing : spacing;
                        })
                        .attr('dy', '4')
                        .attr('text-anchor', function(d) {
                            return d.children || d._children ? 'end' : 'start';
                        })
                        .text(function(d) {
                            return d.name + (d.value ? ': ' + d.value : '');
                        })
                        .style('fill-opacity', 0);

                    var maxSpan = Math.max.apply(Math, nodes.map(function(d) {
                        return d.y + maxLabelWidth;
                    }));
                    if (maxSpan + maxLabelWidth + 20 > w) {
                        changeSVGWidth(maxSpan + maxLabelWidth);
                        d3.select(selector).node().scrollLeft = source.y0;
                    }

                    var nodeUpdate = node.transition()
                        .duration(transitionDuration)
                        .ease(transitionEase)
                        .attr('transform', function(d) {
                            return 'translate(' + d.y + ',' + d.x + ')';
                        });

                    nodeUpdate.select('circle')
                        .attr('r', function(d) {
                            return computeRadius(d);
                        })
                        .style('stroke-width', function(d) {
                            return d.isIdNode ? '2px' : '1px';
                        })
                        .style('stroke', function(d) {
                            return d.isIdNode ? '#F7CA18' : '#4ECDC4';
                        })
                        .style('fill', function(d) {
                            if (d.isIdNode) {
                                return d._children ? '#F5D76E' : 'white';
                            } else {
                                return d._children ? '#86E2D5' : 'white';
                            }
                        });

                    nodeUpdate.select('text').style('fill-opacity', 1);

                    var nodeExit = node.exit().transition()
                        .duration(transitionDuration)
                        .ease(transitionEase)
                        .attr('transform', function(d) {
                            return 'translate(' + source.y + ',' + source.x + ')';
                        })
                        .remove();

                    nodeExit.select('circle').attr('r', 0);
                    nodeExit.select('text').style('fill-opacity', 0);

                    var link = svg.selectAll('path.link')
                        .data(links, function(d) {
                            return d.target.id;
                        });

                    link.enter().insert('path', 'g')
                        .attr('class', 'link')
                        .attr('d', function(d) {
                            var o = {
                                x: source.x0,
                                y: source.y0
                            };
                            return diagonal({
                                source: o,
                                target: o
                            });
                        });

                    link.transition()
                        .duration(transitionDuration)
                        .ease(transitionEase)
                        .attr('d', diagonal);

                    link.exit().transition()
                        .duration(transitionDuration)
                        .ease(transitionEase)
                        .attr('d', function(d) {
                            var o = {
                                x: source.x,
                                y: source.y
                            };
                            return diagonal({
                                source: o,
                                target: o
                            });
                        })
                        .remove();

                    nodes.forEach(function(d) {
                        d.x0 = d.x;
                        d.y0 = d.y;
                    });
                }

                function computeRadius(d) {
                    if (d.children || d._children) {
                        return minRadius + (numEndNodes(d) / scalingFactor);
                    } else {
                        return minRadius;
                    }
                }

                function numEndNodes(n) {
                    var num = 0;
                    if (n.children) {
                        n.children.forEach(function(c) {
                            num += numEndNodes(c);
                        });
                    } else if (n._children) {
                        n._children.forEach(function(c) {
                            num += numEndNodes(c);
                        });
                    } else {
                        num++;
                    }
                    return num;
                }

                function click(d) {
                    if (d.children) {
                        d._children = d.children;
                        d.children = null;
                    } else {
                        d.children = d._children;
                        d._children = null;
                    }

                    update(d);

                    // fast-forward blank nodes
                    if (d.children) {
                        d.children.forEach(function(child) {
                            if (child.isBlankNode && child._children) {
                                click(child);
                            }
                        });
                    }
                }

                function collapse(d) {
                    if (d.children) {
                        d._children = d.children;
                        d._children.forEach(collapse);
                        d.children = null;
                    }
                }

                update(root);
            }

            if (typeof module !== 'undefined' && module.exports) {
                module.exports = jsonldVis;
            } else {
                d3.jsonldVis = jsonldVis;
            }
        })();
    </script>
    <script type="text/javascript">
        var data = %(json_string)s
        d3.jsonldVis(data, '#graph', {
            w: 800,
            h: 600,
            maxLabelWidth: 250
        });
    </script>
</body>

</html>
'''

def visualise(json_data):
    json_string = '''
{
    "@id": "http://example.com/article",
    "@type": "ScholarlyArticle",

    "name": "article title",

    "about": {
        "@id": "http://id.nlm.nih.gov/mesh/D007251",
        "@type": "InfectiousDisease",
        "name": "Influenza, Human",
        "description": "An acute viral infection in humans involving the respiratory tract. It is marked by inflammation of the NASAL MUCOSA; the PHARYNX; and conjunctiva, and by headache and severe, often generalized, myalgia.",
        "code": {
            "@type": "MedicalCode",
            "codeValue": "D007251",
            "codingSystem": "MeSH"
        },
        "mainEntityOfPage": {
            "@id": "#Discussion"
        }
    },

    "author": {
        "@type": "ContributorRole",

        "author": {
            "@id": "http://example.com/peter",
            "@type": "Person",
            "affiliation": [{
                "@id": "http://www.princeton.edu",
                "@type": "CollegeOrUniversity"
            }, {
                "@id": "http://www.harvard.edu/",
                "@type": "CollegeOrUniversity"
            }]
        },

        "roleAffiliation": {
            "@id": "http://www.princeton.edu",
            "@type": "CollegeOrUniversity"
        },

        "sponsor": {
            "@type": "SponsorRole",
            "sponsor": {
                "@type": "Organization"
            },
            "roleOffer": {
                "@type": "FundingSource",
                "serialNumber": "grantId"
            },
            "startDate": "2015-01-01"
        },

        "roleComment": [{
                "@type": "Comment",
                "text": "senior author on this work",
                "about": {
                    "@type": "CreateAction"
                }
            },

            {
                "@type": "Comment",
                "text": "wrote the article",
                "about": {
                    "@type": "WriteAction"
                }
            },

            {
                "@type": "DisclosureStatement",
                "text": "received personal fees for consulting for: Pfizer Inc - New York, NY, USA.",
                "about": {
                    "@type": "PayAction",
                    "agent": {
                        "@type": "Corporation",
                        "name": "Pfizer"
                    }
                }
            },

            {
                "@type": "AcknowledgementStatement",
                "text": "acknowledge the proofreading work of: Bush, Vannevar Vannevar Bush",
                "about": {
                    "@type": "ReadAction",
                    "agent": {
                        "@type": "Person",
                        "name": "Vannevar Bush"
                    }
                }
            }
        ]
    },

    "hasPart": [{
        "@id": "http://example.com/image",
        "@type": "Image",
        "alternateName": "figure 1",
        "caption": "Growth of X as a function of Y",
        "encoding": [{
            "@id": "http://example.com/encodingsmall",
            "@type": "ImageObject",
            "contentUrl": "http://example.com/small",
            "height": "400px",
            "width": "400px",
            "isBasedOnUrl": "http://example.com/encodinglarge"
        }, {
            "@id": "http://example.com/encodinglarge",
            "@type": "ImageObject",
            "contentUrl": "http://example.com/large",
            "height": "1200px",
            "width": "1200px"
        }],
        "isBasedOnUrl": "http://example.com/code"
    }, {
        "@id": "http://example.com/code",
        "@type": "SoftwareSourceCode",
        "codeRepository": "http://example.com/repository"
    }],

    "sponsor": {
        "@type": "SponsorRole",
        "sponsor": {
            "@type": "Organization"
        },
        "roleOffer": {
            "@type": "FundingSource",
            "serialNumber": "grantId"
        },
        "startDate": "2015-01-01"
    },

    "isPartOf": {
        "@id": "issueId",
        "@type": "PublicationIssue",
        "issueNumber": 10,
        "isPartOf": {
            "@id": "volumeId",
            "@type": "PublicationVolume",
            "volumeNumber": 2,
            "isPartOf": {
                "@id": "periodicalId",
                "@type": "Periodical"
            }
        }
    },

    "citation": [{
            "@type": "ScholarlyArticle",
            "name": "On the effect of X on Y",
            "author": {
                "@type": "Person",
                "givenName": "Peter",
                "familyName": "Smith",
                "additionalName": "Jon",
                "name": "Peter J Smith"
            },
            "isPartOf": {
                "@type": "PublicationIssue",
                "issueNumber": 4,
                "isPartOf": {
                    "@type": "PublicationVolume",
                    "volumeNumber": 7,
                    "isPartOf": {
                        "@type": "Periodical",
                        "name": "Journal of metaphysics"
                    }
                }
            },
            "pageStart": "615",
            "pageEnd": "620",
            "datePublished": {
                "@type": "xsd:gYear",
                "@value": 2015
            }
        },

        {
            "@id": "http://example.com/article",
            "@type": "Webpage",
            "name": "How much does 'typesetting' cost?",
            "author": {
                "@type": "Person",
                "givenName": "James",
                "familyName": "Sullivan",
                "name": "James Sullivan"
            },
            "datePublished": {
                "@value": "2015-06-11",
                "@type": "xsd:date"
            },
            "potentialAction": {
                "@type": "ReadAction",
                "actionStatus": "CompletedActionStatus",
                "endTime": {
                    "@value": "2015-06-11",
                    "@type": "xsd:date"
                }
            }
        }
    ],

    "potentialAction": [{
            "@type": "ReadAction",
            "expectsAcceptanceOf": {
                "@type": "Offer",
                "potentialAction": {
                    "@type": "PayAction",
                    "price": "100USD"
                }
            }
        },

        {
            "@type": "ReviewAction",
            "agent-input": {
                "@type": "PropertyValueSpecification",
                "valueRequired": true
            },
            "resultReview-input": {
                "@type": "PropertyValueSpecification",
                "valueRequired": true
            },
            "target": {
                "@type": "EntryPoint",
                "httpMethod": "PUT",
                "urlTemplate": "http://example.com/review"
            }
        },


        {
            "@type": "AddAction",
            "targetCollection": {
                "@id": "issueId",
                "@type": "PublicationIssue",
                "issueNumber": 10,
                "isPartOf": {
                    "@id": "volumeId",
                    "@type": "PublicationVolume",
                    "volumeNumber": 2,
                    "isPartOf": {
                        "@id": "periodicalId",
                        "@type": "Periodical",
                        "name": "Tiqqun"
                    }
                }
            }
        }
    ]
}
    '''
    # json_string = json.dumps(json_data, indent=4)

    with NamedTemporaryFile(delete=False, suffix=".html") as tempf:
        data = TEMPLATE % locals()
        tempf.write(bytes(data, 'UTF-8'))
        logging.debug("Opening %s", tempf.name)
        tempf.flush()

        webbrowser.open('file://' + tempf.name, new=0, autoraise=True)
