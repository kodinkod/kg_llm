#https://github.com/Daniil193/Simple_KG/blob/master/script_for_graph.py
# дополнительные переменные текста для построение html страницы 

header_text = r"""<!doctype html>
                  <html lang="ru">
                    <head>
                    <meta charset="utf-8"/>
                    <title>Interractive graph</title>
                    <style>
                      .parent > div {
                        background: #eee;
                        float: left;
                        margin-right: 2%;
                        padding: 10px;
                        border: 1px solid #ccc;
                        -webkit-box-sizing: border-box;
                        -moz-box-sizing: border-box;
                        box-sizing: border-box;
                      }
                      #all_information{
                        overflow-y:scroll;
                        overflow-x:scroll;
                      }
                      #mynetwork {
                          width: 1600px;
                          height: 800px;
                          border: 1px solid lightgray;
                      }
                      table, td,th {
                        border: 1px solid black; 
                        border-collapse: collapse;
                      }
                    </style>
                    </head>
                    <body>
                    
                    <div class="parent">
                        <div id="mynetwork"></div>
                        <div id="all_information"></div>
                    </div>
                    
                    <link rel="stylesheet" type="text/css" href="https://cdnjs.cloudflare.com/ajax/libs/vis/4.21.0/vis.min.css">
                    <script src="https://visjs.github.io/vis-network/standalone/umd/vis-network.min.js"></script>
                    <script>"""

tail_text = """
      var container = document.getElementById('mynetwork');
      var data = {
        nodes: nodes,
        edges: edges
      };
      var options = {
        "physics":{
          "barnesHut":{
            "gravitationalConstant": -4000, 
            "springConstant": 0.006,
            "damping":0.2
          },
          "repulsion":{"nodeDistance":300}
        }
      };

    var network = new vis.Network(container, data, options);
    var res_container = document.getElementById('all_information');

    network.on( 'click', function(properties) {
        var clickedNodes = nodes.get(properties.nodes);
        var clickedEdges = edges.get(properties.edges);
        var clickedObject;

        if (clickedNodes.length==0 & clickedEdges.length==0){
            console.log("")
            } else {
                    clickedObject = clickedEdges[0] 
                    var total_sum_by_doctype = clickedObject['info'];
                    var tsbd_labels = Object.keys(total_sum_by_doctype);
                    var tsbd_values = Object.values(total_sum_by_doctype);
                    createTable(tsbd_labels, tsbd_values);
                    } 
    });

    function createTable(labels, values){
      var table = document.getElementById('text_information');
      if (table != null)
      {
        table.remove(table);
        table = document.createElement('table');
        table.setAttribute('id', 'text_information');
        res_container.appendChild(table);
      }
      else{
        table = document.createElement('table');
        table.setAttribute('id', 'text_information');
        res_container.appendChild(table);
      }
      var tr_header = document.createElement('tr');
      var th_col_label = document.createElement('th');
      th_col_label.innerHTML = "Номер";
      var th_col_value = document.createElement('th');
      th_col_value.innerHTML = "Предложение, которое содержит ребро";
      tr_header.appendChild(th_col_label);
      tr_header.appendChild(th_col_value);
      table.appendChild(tr_header);

      for (var i=0; i < labels.length; i++){
        var tr = document.createElement('tr');
        let td1 = document.createElement('td');
        td1.innerHTML = labels[i]
        let td2 = document.createElement('td');
        td2.innerHTML = values[i]
        tr.appendChild(td1);
        tr.appendChild(td2);
        table.appendChild(tr);
      }
    }


    </script>
    <style>
      #all_information {
        overflow-y:scroll;
      }
    </style>
    </body>
    </html>"""