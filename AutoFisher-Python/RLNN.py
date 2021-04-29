import math
import numpy as np
from numpy.core.defchararray import array
import Optimizers as optimizers
import pickle
import sys, random

######################################################################
# class NeuralNetwork()
######################################################################

class RLNeuralNetwork():

    def __init__(self, validActions, Epsilon, n_inputs, n_hiddens_per_layer, n_outputs, activation_function='tanh'):
        self.validActions = validActions
        self.Epsilon = Epsilon
        self.n_inputs = n_inputs
        self.n_outputs = n_outputs
        self.activation_function = activation_function

        # Set self.n_hiddens_per_layer to [] if argument is 0, [], or [0]
        if n_hiddens_per_layer == 0 or n_hiddens_per_layer == [] or n_hiddens_per_layer == [0]:
            self.n_hiddens_per_layer = []
        else:
            self.n_hiddens_per_layer = n_hiddens_per_layer

        # Initialize weights, by first building list of all weight matrix shapes.
        n_in = n_inputs
        shapes = []
        for nh in self.n_hiddens_per_layer:
            shapes.append((n_in + 1, nh))
            n_in = nh
        shapes.append((n_in + 1, n_outputs))

        # self.all_weights:  vector of all weights
        # self.Ws: list of weight matrices by layer
        self.all_weights, self.Ws = self.make_weights_and_views(shapes)

        # Define arrays to hold gradient values.
        # One array for each W array with same shape.
        self.all_gradients, self.dE_dWs = self.make_weights_and_views(shapes)

        self.trained = False
        self.total_epochs = 0
        self.error_trace = []
        self.Xmeans = None
        self.Xstds = None
        self.Tmeans = None
        self.Tstds = None

    def make_weights_and_views(self, shapes):
        # vector of all weights built by horizontally stacking flatenned matrices
        # for each layer initialized with uniformly-distributed values.
        all_weights = np.hstack([np.random.uniform(size=shape).flat / np.sqrt(shape[0])
                                 for shape in shapes])
        # Build list of views by reshaping corresponding elements from vector of all weights
        # into correct shape for each layer.
        views = []
        start = 0
        for shape in shapes:
            size = shape[0] * shape[1]
            views.append(all_weights[start:start + size].reshape(shape))
            start += size
        return all_weights, views

    # Return string that shows how the constructor was called
    def __repr__(self):
        return f'{type(self).__name__}({self.n_inputs}, {self.n_hiddens_per_layer}, {self.n_outputs}, \'{self.activation_function}\')'

    # Return string that is more informative to the user about the state of this neural network.
    def __str__(self):
        result = self.__repr__()
        if len(self.error_trace) > 0:
            return self.__repr__() + f' trained for {len(self.error_trace)} epochs, final training error {self.error_trace[-1]:.4f}'

    def train(self, X, T, n_epochs, learning_rate, method='sgd', verbose=True): #I removed the Xmeans check to force pre-calculation.
        # Standardize X and T
        X = (X - self.Xmeans) / self.Xstds
        T = (T - self.Tmeans) / self.Tstds

        # Instantiate Optimizers object by giving it vector of all weights
        optimizer = optimizers.Optimizers(self.all_weights)

        # Define function to convert value from error_f into error in original T units,
        # but only if the network has a single output. Multiplying by self.Tstds for
        # multiple outputs does not correctly unstandardize the error.
        if len(self.Tstds) == 1:
            error_convert_f = lambda err: (np.sqrt(err) * self.Tstds)[0]  # to scalar
        else:
            error_convert_f = lambda err: np.sqrt(err)[0]  # to scalar

        if method == 'sgd':

            error_trace = optimizer.sgd(self.error_f, self.gradient_f,
                                        fargs=[X, T], n_epochs=n_epochs,
                                        learning_rate=learning_rate,
                                        error_convert_f=error_convert_f)

        elif method == 'adam':

            error_trace = optimizer.adam(self.error_f, self.gradient_f,
                                         fargs=[X, T], n_epochs=n_epochs,
                                         learning_rate=learning_rate,
                                         error_convert_f=error_convert_f)

        else:
            raise Exception("method must be 'sgd' or 'adam'")

        self.error_trace = error_trace

        # Return neural network object to allow applying other methods after training.
        #  Example:    Y = nnet.train(X, T, 100, 0.01).use(X)
        return self

    def relu(self, s):
        s[s < 0] = 0
        return s

    def grad_relu(self, s):
        return (s > 0).astype(int)

    def forward_pass(self, X):
        '''X assumed already standardized. Output returned as standardized.'''
        self.Ys = [X]
        for W in self.Ws[:-1]:
            if self.activation_function == 'relu':
                self.Ys.append(self.relu(self.Ys[-1] @ W[1:, :] + W[0:1, :]))
            else:
                self.Ys.append(np.tanh(self.Ys[-1] @ W[1:, :] + W[0:1, :]))
        last_W = self.Ws[-1]
        self.Ys.append(self.Ys[-1] @ last_W[1:, :] + last_W[0:1, :])
        return self.Ys

    # Function to be minimized by optimizer method, mean squared error
    def error_f(self, X, T):
        Ys = self.forward_pass(X)
        mean_sq_error = np.mean((T - Ys[-1]) ** 2)
        return mean_sq_error

    # Gradient of function to be minimized for use by optimizer method
    def gradient_f(self, X, T):
        '''Assumes forward_pass just called with layer outputs in self.Ys.'''
        error = T - self.Ys[-1]
        n_samples = X.shape[0]
        n_outputs = T.shape[1]
        delta = - error / (n_samples * n_outputs)
        n_layers = len(self.n_hiddens_per_layer) + 1
        # Step backwards through the layers to back-propagate the error (delta)
        for layeri in range(n_layers - 1, -1, -1):
            # gradient of all but bias weights
            self.dE_dWs[layeri][1:, :] = self.Ys[layeri].T @ delta
            # gradient of just the bias weights
            self.dE_dWs[layeri][0:1, :] = np.sum(delta, 0)
            # Back-propagate this layer's delta to previous layer
            if self.activation_function == 'relu':
                delta = delta @ self.Ws[layeri][1:, :].T * self.grad_relu(self.Ys[layeri])
            else:
                delta = delta @ self.Ws[layeri][1:, :].T * (1 - self.Ys[layeri] ** 2)
        return self.all_gradients

    def use(self, X):
        '''X assumed to not be standardized'''
        # Standardize X
        X = (X - self.Xmeans) / self.Xstds
        Ys = self.forward_pass(X)
        Y = Ys[-1]
        # Unstandardize output Y before returning it
        return Y * self.Tstds + self.Tmeans



    def dump(self, dumpTo):
        pickle.dump(self, open(dumpTo, "wb"))

    @staticmethod
    def load(dumpFile):
        return pickle.load(dumpFile)

    def createStandards(self, Xmeans, Xstds, Tmeans, Tstds):
        self.Xmeans = np.array(Xmeans)
        self.Xstds = np.array(Xstds)
        self.Tmeans = np.array(Tmeans)
        self.Tstds = np.array(Tstds)


    def EpsilonGreedyUse(self, state):   
        if np.random.uniform() < self.Epsilon:
            action = np.random.choice(self.validActions)
            
        else:
            actions_randomly_ordered = random.sample(self.validActions, len(self.validActions))
            Qs = [self.use(np.array([state+[a]])) for a in actions_randomly_ordered]
            ai = np.argmin(Qs)
            action = actions_randomly_ordered[ai]
            
        Q = self.use(np.array([state + [action]]))
        
        return action, Q   # return the chosen action and Q(state, action)

    #(Try to minimize this; the best case is #0 and the worst is case #-1):
    #returns:
    #r1: 0 if posA==posB (deltaP == 0) AND velA==velB (deltaV==0)
    #r2: 1 if posA==posB (deltaP == 0) AND velA!=velB (deltaV != 0)
    #r3: 2 if posA!=posB (deltaP != 0) AND deltaV < 0 (approaching target)
    #r4: 3 if posA!=posB (deltaP != 0) and velA==velB (deltaV == 0)
    #reasoning:
    #r1: obvious. moving together is exactly what we want
    #r2: getting close... we are at the same position but are moving away.
    #r3: we arent at the same posiiton, BUT our velocities are such that the bobber is approaching the fish.
    #r4: the worst case: not at same postion AND not getting any closer.

    @staticmethod
    def getReinforcement(state):
        bobberPos, fishPos, bobberVel, fishVel = state
        
        relPos = fishPos - bobberPos
        range = abs(relPos)
        # relVel = abs(fishVel - bobberVel)
        vSign = bobberVel * fishVel

        bColliding = (range <= 75)

        if(bColliding):
            if(vSign < 0):
                #moving away and colliding
                return 1
            elif (vSign > 0):
                #moving together and colliding
                return 0
            else:
                #not moving and colliding
                return 0
            return 100
        else:
            relPosVelSign = bobberVel * relPos
            if(relPosVelSign < 0):
                #moving away from fish and not colliding
                return 4
            elif(relPosVelSign > 0):
                #moving towards fish and not colliding
                return 2
            else:
                #not moving and not colliding
                return 3



            return 100
        
        
        
        # deltaP, deltaV = state
        # if(deltaP==0 and deltaV==0):
        #     return 0
        # elif(deltaP==0 and deltaV!=0):
        #     return 1
        # elif(deltaP!=0 and deltaV<0):
        #     return 2
        # elif(deltaP!=0 and deltaV==0):
        #     return 3
        # return 100




