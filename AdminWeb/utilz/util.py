

def fetch_all_json(result):
  lis = []

  for row in result.fetchall():
    i =0
    dic = {}  
    
    for data in row:
      # if(len(result.keys())
      # print(len(result.keys()))
      # print(i)
      # print(data)
      dic[result.keys()[i]] = str(data)
      if i == len(row)-1:
        lis.append(dic)

      i=i+1
  return lis