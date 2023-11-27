from random import randint


class individual:
	def __init__(self) -> None:
		self.gnome = ""
		self.fitness = 0

	def __lt__(self, other):
		return self.fitness < other.fitness

	def __gt__(self, other):
		return self.fitness > other.fitness



best_fitness_values = []
avg_fitness_values = []

class TSP():

  number_gen = 0
  def __init__(self, matrix, START, POP_SIZE, INT_MAX):
    self.V = len(matrix)
    self.START = START
    self.INT_MAX = INT_MAX
    self.POP_SIZE = POP_SIZE
    self.solution = self.run(matrix)

  def run(self, mp):
    POP_SIZE = self.POP_SIZE
    gen = 1
    gen_thres = 200
    last_best_fitness = 0
    Threshold_generation_same_fitness = 20
    number_gen = 0
    population = []
    temp = individual()

    for i in range(POP_SIZE):
      temp.gnome = self.create_gnome()
      temp.fitness = self.cal_fitness(temp.gnome,mp)
      population.append(temp)
    found = False
    while gen <= gen_thres:
      population.sort()
      new_population = population
      first = int(8*POP_SIZE/100)
      second = first+int(28*POP_SIZE/100)
      for i in range(POP_SIZE):
        if i <= first:
          new_gnome = individual()
          new_gnome.gnome = self.create_gnome()
          new_gnome.fitness = self.cal_fitness(new_gnome.gnome,mp)
          if self.notExist(new_gnome, new_population):
            new_population.append(new_gnome)
        elif i <= second:
          rand_index = self.rand_num(0, POP_SIZE)
          new_g = self.mutatedGene(population[rand_index].gnome)
          new_gnome = individual()
          new_gnome.gnome = new_g
          new_gnome.fitness = self.cal_fitness(new_gnome.gnome,mp)
          if self.notExist(new_gnome, new_population):
            new_population.append(new_gnome)
        else:
          while True:
            r1 = self.rand_num(0,POP_SIZE)
            r2 = self.rand_num(0,POP_SIZE)
            if r1 != r2:
              new_gnome = individual()
              new_gnome.gnome = self.cross_over(population[r1].gnome,population[r2].gnome)
              new_gnome.fitness = self.cal_fitness(new_gnome.gnome, mp)
              if self.notExist(new_gnome, new_population):
                new_population.append(new_gnome)
              break



      new_population.sort()
      population = new_population[0:POP_SIZE]
      if last_best_fitness == population[0].fitness:
        number_gen += 1
      else:
        last_best_fitness = population[0].fitness
        number_gen = 0
      if number_gen == Threshold_generation_same_fitness:
        return population[0].gnome
        break
      gen += 1
    return population[0].gnome


  def rand_num(self, start, end):
    return randint(start, end-1)



  def repeat(self, s, ch):
    splitted = s.split("|")
    for i in splitted :
      if i == ch :
        return True
    return False


  def mutatedGene(self, gnome):
    V = self.V
    splitted = gnome.split("|")
    while True:
      r = self.rand_num(1,V)
      r1 = self.rand_num(1,V)
      if r1 != r:
        temp = splitted[r]
        splitted[r] = splitted[r1]
        splitted[r1] = temp
        break
    return '|'.join(splitted)

  def create_gnome(self):
    V = self.V
    START = self.START
    gnome = str(START)+ "|"
    index = 0
    while True:
      # if index == V-1:
      #   gnome += gnome[0]
      #   break
      if index == V-1:
        gnome = gnome[:-1]
        break

      temp = self.rand_num(1, V)
      # if temp == START:
      #   continue

      if not self.repeat(gnome, str(temp)):
        gnome += str(temp)+"|"
        index += 1

    return gnome


  def cal_fitness(self, gnome,mp):
    f= 0
    INT_MAX = self.INT_MAX
    splitted = gnome.split("|")
    for i in range(len(splitted)-1):
      if mp[int(splitted[i])][int(splitted[i + 1])] == INT_MAX:
        return INT_MAX
      f += mp[int(splitted[i])][int(splitted[i + 1])]
    return f


  def cross_over(self, parent1, parent2):
    START = self.START
    V = self.V
    x = self.rand_num(1, V-1)
    y = self.rand_num(x+1, V)
    split_parent1 = parent1.split("|")
    split_parent2 = parent2.split("|")
    sub1 = list(split_parent1[x:y+1])
    sub2 = []
    for i in range(1, len(split_parent2)):
      if split_parent2[i] not in sub1:
        sub2.append(split_parent2[i])
    if sub2:
      child = str(START) + "|" + "|".join(sub1) + "|" + "|".join(sub2)
    else:
      child = str(START) + "|" + "|".join(sub1)
    return child



  def notExist(self, individ, list_individ):
    for z in list_individ:
      if  z.gnome == individ.gnome:
        return False
    return True


