import pandas
import nn
import numpy
import matplotlib.pyplot as plt

url = "irisDataSet.csv"
print("dataset url: ", url)
dataset = pandas.read_csv(url)

print(dataset.shape)
print(dataset.head(5))
print(dataset.groupby("iris").size())

#shuffle dataset, sorted by default (csv)
dataset = dataset.sample(frac=1).reset_index()

print(dataset.head(5))

#split into  training and test data
training_data = dataset.iloc[:100]
test_data = dataset.iloc[100:]

print("training data: " + str(training_data.shape))
print("test data: " + str(test_data.shape))


# number of input, hidden and output nodes
input_nodes = 4
hidden_nodes = 2
output_nodes = 3

# learning rate
learning_rate = 0.125

# create instance of neural network
n = nn.NeuralNetwork(input_nodes, hidden_nodes, output_nodes, learning_rate)

print("count parameter: " + str(n.getCountParams()))

epochs = 100

overallScore = []

#training iteration
for index_epochs, e in enumerate(range(epochs)):

    for index_row, row in training_data.iterrows():
        inputs = numpy.zeros(input_nodes)

        inputs[0] = (row['sepal length'] / dataset.max()['sepal length'] * 0.99) + 0.01
        inputs[1] = (row['sepal width'] / dataset.max()['sepal width'] * 0.99) + 0.01
        inputs[2] = (row['petal length'] / dataset.max()['petal length'] * 0.99) + 0.01
        inputs[3] = (row['petal width'] / dataset.max()['petal width'] * 0.99) + 0.01

        targets = numpy.zeros(output_nodes) + 0.01
        if(row['iris'] == 'Iris-setosa'):
            targets[0] = 0.99
        if(row['iris'] == 'Iris-versicolor'):
            targets[1] = 0.99
        if(row['iris'] == 'Iris-virginica'):
            targets[2] = 0.99

        # print("e#" + str(index_epochs) + " row#" + str(index_row) + "\tinputs: " + str(inputs) + "\ttargets:" + str(targets))

        n.train(inputs, targets)

    scorecard = []
    # test iteration
    if(index_epochs % 2 == 0):

        for index_row, row in test_data.iterrows():
            inputs = numpy.zeros(input_nodes)

            inputs[0] = (row['sepal length'] / dataset.max()['sepal length'] * 0.99) + 0.01
            inputs[1] = (row['sepal width'] / dataset.max()['sepal width'] * 0.99) + 0.01
            inputs[2] = (row['petal length'] / dataset.max()['petal length'] * 0.99) + 0.01
            inputs[3] = (row['petal width'] / dataset.max()['petal width'] * 0.99) + 0.01

            if (row['iris'] == 'Iris-setosa'):
                correct_label = 0
            if (row['iris'] == 'Iris-versicolor'):
                correct_label = 1
            if (row['iris'] == 'Iris-virginica'):
                correct_label = 2

            result = n.query(inputs)
            label = numpy.argmax(result)

            # print("###")
            # print("input:\t" + str(inputs))
            # print("output:\n" + str(result))
            # print("guessed label:\t", label)
            # print("correct label:\t", correct_label)

            if (label == correct_label):
                # network's answer matches correct answer, add 1 to scorecard
                scorecard.append(1)
            else:
                # network's answer doesn't match correct answer, add 0 to scorecard
                scorecard.append(0)


        scorecard_array = numpy.asarray(scorecard)
        print("\n" + str(index_epochs) + "/" + str(epochs) + " trained")
        print("accuracy: " + str(scorecard_array.sum() / scorecard_array.size))

        overallScore.append([index_epochs, scorecard_array.sum() / scorecard_array.size])


x, y = numpy.array(overallScore).T
plt.plot(x, y)
plt.xlabel('epochs')
plt.ylabel('accuracy')
plt.grid(True)
plt.show()