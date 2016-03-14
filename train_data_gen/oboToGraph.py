from random import shuffle
import random
import numpy as np
import cPickle as pickle

total=0
marked={}
def dfs(graph, h, v):
	global total
	marked[v]=True
	if len( graph[v]['names'] ) > 1:
		total+=1
	for u in graph[v]['kids']:
		if u not in marked:
			h[u]=h[v]+1
			dfs(graph, h, u)

def bfs(g, start, lower, upper):
	que=[start]
	d={}
	d[start]=0
	visited={}
	visited[start]=True
	tail=0
	local=[]
	while tail < len(que):
		v=que[tail]
		if d[v] > upper:
			break
		for u in g[v]:
			if u not in visited:
				d[u]=d[v]+1
				que.append(u)
				if d[u]>=lower:
					local.append(u)
				visited[u]=True
		tail+=1
	return local

def randomize_triplet(t):
	new_t = [x for x in t] #.append(0)
	new_t.append(np.array([1.0, 0.0]))
	if random.random() > 0.5:
		new_t[1], new_t[2] = new_t[2], new_t[1]
		new_t[3] = np.array([0.0, 1.0])
	return new_t


def embed_phrase(phrase, wordList, padded_size):
	words=phrase.lower().strip().split()	
	#for w in words:
	em_list = [wordList[w] for w in words]
	em_list += [np.zeros(wordList["the"].shape)]*(padded_size-len(words))
	embeding = np.concatenate(em_list)
	return embeding

def check_phrase(phrase, wordList, word_limit):	
	words=phrase.lower().strip().split()	
	if len(words) <= word_limit and all([(w in wordList) for w in words]):
		return True
	return False


def main():
	oboFile=open("hp.obo")
	vectorFile=open("test_vectors.txt")

	wordVector={}
	for line in vectorFile:
		tokens = line.strip().split(" ")
		wordVector[tokens[0]] = np.array(map(float,tokens[1:]))
	
	graph={}
	neighbour={}
	while True:
		line=oboFile.readline()
		if line == "":
			break
		tokens=line.strip().split(" ")
		if tokens[0]=="id:":
			hp_id=tokens[1]
			graph[hp_id] = {}
			neighbour[hp_id] = []
			graph[hp_id]['kids'] = []

		if tokens[0] == "name:":
			graph[hp_id]['names'] = [' '.join(tokens[1:])]
		if tokens[0] == "synonym:":
			last_index = (i for i,v in enumerate(tokens) if v.endswith("\"")).next()
			graph[hp_id]['names'].append( ' '.join(tokens[1:last_index+ 1]).strip("\"") )

	oboFile.seek(0)
	while True:
		line=oboFile.readline()
		if line == "":
			break
		tokens=line.strip().split(" ")
		if tokens[0]=="id:":
			hp_id=tokens[1]

		if tokens[0]=="is_a:":
			graph[tokens[1]]['kids'].append(hp_id)
			neighbour[tokens[1]].append(hp_id)
			neighbour[hp_id].append(tokens[1])

	nearby_close={}
	nearby_mid={}
	nearby_far={}
	for v in neighbour:
		nearby_close[v]=bfs(neighbour, v, 1, 1)
		nearby_mid[v]=bfs(neighbour, v, 2, 2)
		nearby_far[v]=bfs(neighbour, v, 3, 5)

	irreleventRelevent_triplets = []

	count_close_far=0
	count_close_mid=0
	count_syn_close=0
	for v in graph.keys():
		if len(neighbour[v]) == 0:
			continue
		for t in range(10):
			relevant_concept = random.choice(nearby_close[v])
			irrelevant_concept = random.choice(nearby_far[v])
			#irreleventRelevent_triplets.append([random.choice(graph[v]['names']), random.choice(graph[relevant_concept]['names']), random.choice(graph[irrelevant_concept]['names'])])
			irreleventRelevent_triplets.append([ random.choice(graph[concept]['names']) for concept in [v, relevant_concept, irrelevant_concept] ])
			count_close_far+=1
		for t in range(10):
			relevant_concept = random.choice(nearby_close[v])
			irrelevant_concept = random.choice(nearby_mid[v])
			irreleventRelevent_triplets.append([ random.choice(graph[concept]['names']) for concept in [v, relevant_concept, irrelevant_concept] ])
			count_close_mid+=1

		for x_name1 in graph[v]['names']:
			for x_name2 in graph[v]['names']:
				if x_name1 == x_name2:
					continue
				for t in range(3):
					irrelevant_concept = random.choice(nearby_close[v])
					irreleventRelevent_triplets.append([x_name1, x_name2, random.choice(graph[irrelevant_concept]['names'])])
					count_syn_close+=1
				for t in range(1):
					irrelevant_concept = random.choice(nearby_mid[v])
					irreleventRelevent_triplets.append([x_name1, x_name2, random.choice(graph[irrelevant_concept]['names'])])
					count_syn_close+=1

	shuffle(irreleventRelevent_triplets)
	print len(irreleventRelevent_triplets)
	word_limit=10

	filtered_triplets = [triplet for triplet in irreleventRelevent_triplets if all([check_phrase(phrase, wordVector, word_limit) for phrase in triplet])]
	pickle.dump(filtered_triplets, open("raw_triplets","wb"))
	print len(filtered_triplets)
	print (filtered_triplets[0])
	vectorized_triplets = [ [embed_phrase(phrase, wordVector, word_limit) for phrase in triplet] for triplet in filtered_triplets ]
	randomized_triplets = map( randomize_triplet, vectorized_triplets )
	pickle.dump(randomized_triplets, open("triplets","wb"))
	#pickle.dump(randomized_triplets[:10000], open("triplets","wb"))
	
if __name__ == "__main__":
	main()
