import numpy as np

class JointPDF():

    def __init__(self, data, labels, is_normalized=True):
        """Constructor.

        Keyword arguments:
        data -- numpy ndimensional array with joint pdf data values
        labels -- list of labels for each data dimension
        """

        """Checking the data"""
        assert len(data) > 0, "Empty data provided."
        assert len(data.shape) == len(labels), "Data dimensions must be the same length as labels " + str(len(data))
        assert 0.0 <= data.all() <= 1.0, 'Joint probability must be within [0, 1] ' + str(data)
        if is_normalized:
            try:
                np.testing.assert_almost_equal(np.sum(data), 1.0)
            except AssertionError as e:
                print 'All joint probabilities must sum 1.'
                raise AssertionError(e)

        self.labels = labels
        self.joint_probabilities = np.array(data)

        self.num_bins = self.joint_probabilities.shape
        self.num_variables = len(self.num_bins)
        self.is_normalized = is_normalized


    def get_all_labels(self):
        """Returns the labels.
        """    
        return self.labels


    def get_labels(self, base_labels):
        """Returns the labels that fits with base_label + "_xxxxx".
        """
        if base_labels == "":
            return self.labels
        if np.isscalar(base_labels):
            base_labels = [base_labels]
        return [o_l for l in base_labels for o_l in self.labels if o_l.startswith(l + "_") or o_l == l]

    def get_num_variables(self):
        """Returns the number of variables.
        """    
        return self.num_variables


    def get_num_bins(self):
        """Returns the number of bins.
        """    
        return self.num_bins

    def get_num_bins_of(self, label):
        """Returns the number of bins of label.
        """
        assert np.isscalar(label), "Function get_num_bins_of only allows one label."
        return self.num_bins[self.labels.index(label)]

    def get_joint_probability(self, values_idcs):
        """Gets the values from the matrix.

        Keyword arguments:
        values_idcs -- the indices of the values
        """    
        assert len(values_idcs) == self.num_variables, 'One value per variable is mandatory'
        assert values_idcs < self.num_bins, 'Some index is out of range'

        return self.joint_probabilities[tuple(values_idcs)]


    def has_label(self, label):
        """Checks if a label is on the labels list.

        Keyword arguments:
        label -- the label to check
        """    
        return label in self.labels


    def get_label_size(self, label):
        """Returns the size of the label dimension.

        Keyword arguments:
        label -- the label to meassure
        """
        assert self.has_label(label), "Label " + label + " does not exist."
        return self.num_bins[self.labels.index(label)]


    def filter_joint_probabilities(self, labels, indices):
        """Filters the joint probabilities with the data provided.
        The labels that are not specified are left with all its information, the specified are reduced to the values set by the indices.

        Keyword arguments:
        labels -- list of labels to filter
        indices -- list of indices for the desired values (single values or lists can be used) E.g. [[1, 2, 4], 4, [4,9]]
        """
        assert len(labels) == len(indices), "Length of labels and indices must be the same."
        assert all(x in self.labels for x in labels), "Labels " + str(labels) + " must be in " + str(self.labels)

        tmp_joint_prob = self.joint_probabilities
        """Apply the indexing to every label in the list"""
        for l in labels:
            label_idx = self.labels.index(l)
            """Transform  values to list if scalar"""
            if np.isscalar(indices[labels.index(l)]):
                indices[labels.index(l)] = [indices[labels.index(l)]]
            """Slice the dimension"""
            tmp_joint_prob = np.take(tmp_joint_prob, indices[labels.index(l)], axis=label_idx)

        return JointPDF(tmp_joint_prob, self.labels, False)


    def remove_dimensions(self, labels):
        """Removes the joint probability of the chosen labels.
        If only one label is left, the result is the marginals of the variable.

        Keyword arguments:
        labels -- labels to remove
        """
        assert all(x in self.labels for x in labels), "Labels " + str(labels) + " must be in " + str(self.labels)
        assert len(labels) < len(self.labels), "Not allowed to remove all labels."
        assert len(labels) > 0, "No label specified to remove."

        new_labels = [l for i,l in enumerate(self.labels) if l not in labels]
        var_indices = [i for i,l in enumerate(self.labels) if l in labels]

        return JointPDF(np.sum(self.joint_probabilities, axis=tuple(var_indices)), new_labels, self.is_normalized)


    def remove_values(self, labels, indices):
        """Removes the values from the labels specified.
        The result is not a joint PDF.

        Keyword arguments:
        labels -- labels of the values to be removed
        indices -- list of indices for the values to remove (single values or lists can be used) E.g. [[1, 2, 4], 4, [4,9]]
        """
        assert len(labels) == len(indices), "Length of labels and indices must be the same."
        assert all(x in self.labels for x in labels), "Labels " + str(labels) + " must be in " + str(self.labels)

        tmp_joint_prob = self.joint_probabilities
        """Apply the removal to every label in the list separately"""
        for l in labels:
            label_idx = self.labels.index(l)
            """Ensure that the dimension will not be empty"""
            assert np.isscalar(indices[labels.index(l)]) or self.num_bins[label_idx] > len(indices[labels.index(l)])
            tmp_joint_prob = np.delete(tmp_joint_prob, indices[labels.index(l)], axis=label_idx)

        return JointPDF(tmp_joint_prob, self.labels, False)


    def shrink_dimensions_to(self, labels):
        """Shrink the joint probability to the chosen labels.
        If only one label is chosen, the result is the marginals of the variable.

        Keyword arguments:
        labels -- labels to reduce to
        """
        if np.isscalar(labels):
            labels = [labels]
        assert all(x in self.labels for x in labels), "Labels " + str(labels) + " must be in " + str(self.labels)
        assert len(labels) > 0, "No label specified to shrink."

        var_indices = []
        new_labels = []
        for i,l in enumerate(self.labels):
            if l not in labels:
                var_indices.append(i)
            else:
                new_labels.append(l)
        return JointPDF(np.sum(self.joint_probabilities, axis=tuple(var_indices)), new_labels, self.is_normalized)


    def shrink_values_to(self, labels, indices):
        """Shrink the values of the labels specified.
        The result is not a joint PDF.

        Keyword arguments:
        labels -- labels of the values to be removed
        indices -- list of indices for the values to remove (single values or lists can be used) E.g. [[1, 2, 4], 4, [4,9]]
        """
        assert len(labels) == len(indices), "Length of labels and indices must be the same."
        assert all(x in self.labels for x in labels), "Labels " + str(labels) + " must be in " + str(self.labels)

        tmp_joint_prob = self.joint_probabilities
        """Shrink values from the labels"""
        for l in labels:
            label_idx = self.labels.index(l)
            """Transform  values to list if scalar"""
            if np.isscalar(indices[labels.index(l)]):
                indices[labels.index(l)] = [indices[labels.index(l)]]
            """Slice the dimension"""
            tmp_joint_prob = np.take(tmp_joint_prob, indices[labels.index(l)], axis=label_idx)

        """Remove dimensions not specified if any"""
        var_idcs = [i for i,l in enumerate(self.labels) if l not in labels]
        if var_idcs:
            tmp_joint_prob = np.squeeze(tmp_joint_prob, axis=var_idcs)
        return JointPDF(tmp_joint_prob, labels, False)


    def calculate_conditional_probabilities(self, cond_variables):
        """Calculates the joint probabilities given some conditional variables.
        Using formula P(A|B) = P(A and B) / P(B).
        Note that the condition variables are not removed, so all the probability distribution is available. 
        So it is possible to get P(A|B=b1) or P(A|B=b2) accessing directly to the indices of b1 and b2.
        The result is not a joint PDF.

        Keyword arguments:
        cond_variables -- the conditional variables
        """
        assert all(x in self.labels for x in cond_variables), "Labels " + str(cond_variables) + " must be in " + str(self.labels)
        assert len(cond_variables) < len(self.labels), "Condition variables must be lower than the total number of variables."
        assert len(cond_variables) > 0, "No conditional variables specified."

        """Getting the marginals from the condition variables"""
        marginals = self.shrink_dimensions_to(cond_variables).joint_probabilities
        """Before dividing, the marginals have to be ordered and filled to fit current dimension order and size."""
        margIdx = 0
        for l in self.labels:
            if l not in cond_variables:
                marginals = np.expand_dims(marginals, axis=margIdx)
            margIdx += 1

        cond_probs = self.joint_probabilities / marginals
        """Result is returned in a JointPDF class despite is nor a joint probability function"""
        return JointPDF(cond_probs, self.labels, False)

    def normalize(self):
        """Normalizes the probabilities.
        """
        total_prob = np.sum(self.joint_probabilities)
        self.joint_probabilities /= total_prob
        self.is_normalized = True

    def random(self):
        """Generates random normalized probabilities.
        """
        self.joint_probabilities = np.random.random(self.num_bins)
        self.joint_probabilities /= np.sum(self.joint_probabilities)

    def sample_values(self, labels, percentages, sort=False):
        """Samples the values of the selected dimensions. Each dimension is filtered by its values randomly to be reduced the percentage specified.
        Then is normalized

        Keyword arguments:
        labels -- labels of the values to be sampled
        percentages -- list of percentages for the values to sample. Must be within the range (0, 1].
        """
        assert len(labels) > 0, "No labels specified."
        assert len(labels) == len(percentages), "Length of labels and percentages must be the same."
        assert all(p <= 1 and p > 0 for p in percentages), "Percentages must be greater than 0 and lower or equals to 1"

        """Generate random indices for each dimension"""
        indices = []
        for i, l in enumerate(labels):
            index = self.labels.index(l)
            val_size = self.num_bins[index]
            indices_i = np.arange(val_size)
            np.random.shuffle(indices_i)
            indices_i = indices_i[:int(val_size*percentages[i])]
            if sort:
                indices_i = np.sort(indices_i)
            indices.append(indices_i)

        filtered = self.filter_joint_probabilities(labels, indices)
        filtered.normalize()
        return filtered


    def sample_variables(self, labels, percentage):
        """Samples the selected labels. The dimensions will be shrunk in a percentage.
        The result is normalized.

        Keyword arguments:
        labels -- labels of the values to be sampled
        percentage -- percentage to shrink.
        """
        assert len(labels) > 0, "No labels specified."
        assert np.isscalar(percentage), "Percentage parameter should be a single number."
        assert percentage <= 1 and percentage > 0, "Percentage must be greater than 0 and lower or equals to 1"

        if percentage == 1:
            return self

        labels_to_sample = self.get_labels(labels)

        labels_size = len(labels_to_sample)
        np.random.shuffle(labels_to_sample)
        """Get the list of labels that will be removed"""
        labels_to_remove = labels_to_sample[int(labels_size*percentage):]

        """If no label has to be removed return the same object"""
        if not labels_to_remove:
            return self
        return self.remove_dimensions(labels_to_remove)

    def join_dimensions(self, labels, new_label):
        """Joins multiple dimensions in a new one and delete the old ones. 
        It takes all the combinations of the values from the dimensions to delete as values for the new dimension.
        The result is normalized.

        Keyword arguments:
        labels -- labels to join
        new_label -- name for the new label.
        """
        labels = self.get_labels(labels)
        """Create the new dimension"""
        index_new = self.labels.index(labels[0])
        tmp = np.expand_dims(self.joint_probabilities, axis=index_new)
        tmp_labels = self.labels[:]
        tmp_labels.insert(index_new, new_label)
        tmp_bins = self.num_bins
        tmp_bins = list(tmp_bins)
        tmp_bins.insert(index_new, 1)
        for i, l in enumerate(labels):
            index = self.labels.index(labels[i])
            """If the dimensions are separated, move the old dimension near the new one"""
            while abs(index_new - index) > 1:
                if index > index_new:
                    index_desp = index - 1
                else:
                    index_desp = index + 1
                tmp = np.swapaxes(tmp, index, index_desp)
                tmp_labels[index], tmp_labels[index_desp] = tmp_labels[index_desp], tmp_labels[index]
                tmp_bins[index], tmp_bins[index_desp] = tmp_bins[index_desp], tmp_bins[index]
                index = index_desp

            """Join the new dimension with the current one"""
            tmp_bins[index_new] = tmp_bins[index_new] * tmp_bins[index]
            del tmp_bins[index]
            tmp = np.resize(tmp, tuple(tmp_bins))
            tmp_labels.remove(l)

        return JointPDF(tmp, tmp_labels)

    def reorder_dimensions(self, labels_order):
        """Reorder the dimensions to fit the specified order. 

        Keyword arguments:
        labels_order -- labels order.
        """
        assert all(x in self.labels for x in labels_order), "Labels " + str(labels_order) + " must be in " + str(self.labels)

        labels = self.get_labels(labels_order)

        for i, l in enumerate(labels):
            """Swap dimensions when necessary"""
            if l != self.labels[i]:
                index_of_l = self.labels.index(l)
                self.joint_probabilities = np.swapaxes(self.joint_probabilities, i, index_of_l)
                self.labels[i], self.labels[index_of_l] = self.labels[index_of_l], self.labels[i]



