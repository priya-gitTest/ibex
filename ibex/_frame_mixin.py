from __future__ import absolute_import

import operator
import collections

from sklearn import pipeline
from sklearn import exceptions


def _make_pipeline_steps(objs):
    names = [type(o).__name__.lower() for o in objs]
    name_counts = collections.Counter(names)
    name_inds = name_counts.copy()
    unique_names = []
    for name in names:
        if name_counts[name] > 1:
            unique_names.append(name + '_' + str(name_counts[name] - name_inds[name]))
            name_inds[name] -= 1
        else:
            unique_names.append(name)

    return list(zip(unique_names, objs))


class FrameMixin(object):
    """
    A base class for steps taking pandas entities, not numpy entities.

    Subclass this step to indicate that a step takes pandas entities.

    Example:

        This is a simple, illustrative "identity" transformer,
        which simply relays its input.

        >>> from sklearn import base
        >>> import ibex
        >>>
        >>> class Id(
        ...            base.BaseEstimator, # (1)
        ...            base.TransformerMixin, # (2)
        ...            ibex.FrameMixin): # (3)
        ...
        ...     def fit(self, X, _=None):
        ...         self.x_columns = X.columns # (4)
        ...         return self
        ...
        ...     def transform(self, X):
        ...         return X[self.x_columns] # (5)

        Note the following general points:

        1. We subclass :class:`sklearn.base.BaseEstimator`, as this is an estimator.

        2. We subclass :class:`sklearn.base.TransformerMixin`, as, in this case, this is specifically a transformer.

        3. We subclass :class:`ibex.FrameMixin`, as this estimator deals with ``pandas`` entities.

        4. In ``fit``, we make sure to set :py:attr:`ibex.FrameMixin.x_columns`; this will ensure that the
        transformer will "remember" the columns it should see in further calls.

        5. In ``transform``, we first use ``x_columns``. This will verify the columns of ``X``, and also reorder
        them according to the original order seen in ``fit`` (if needed).

        Suppose we define two :class:`pandas.DataFrame` objects, ``X_1`` and ``X_2``, with different columns:

        >>> import pandas as pd
        >>>
        >>> X_1 = pd.DataFrame({'a': [1, 2, 3], 'b': [3, 4, 5]})
        >>> X_2 = X_1.rename(columns={'b': 'd'})

        The following ``fit``-``transform`` combination will work:

        >>> Id().fit(X_1).transform(X_1)
        a  b
        0  1  3
        1  2  4
        2  3  5

        The following ``fit``-``transform`` combination will fail:

        >>> try:
        ...     Id().fit(X_1).transform(X_2)
        ... except KeyError:
        ...     print('caught')
        caught

        The following ``transform`` will fail, as the estimator was not fitted:

        >>> from sklearn import exceptions
        >>> try:
        ...     Id().transform(X_2)
        ... except exceptions.NotFittedError:
        ...     print('caught')
        caught

        Steps can be piped into each other:

        >>> (Id() | Id()).fit(X_1).transform(X_1)
        a  b
        0  1  3
        1  2  4
        2  3  5

        Steps can be added:

        >>> (Id() + Id()).fit(X_1).transform(X_1)
        a  b  a  b
        0  1  3  1  3
        1  2  4  2  4
        2  3  5  3  5
    """

    @property
    def x_columns(self):
        """
        The columns set in the last call to fit.

        Set this property at fit, and call it in other methods:

        """
        # Tmp Ami - check this
        try:
            return self.__cols
        except AttributeError:
            raise exceptions.NotFittedError()

    @x_columns.setter
    def x_columns(self, columns):
        self.__cols = columns

    def __or__(self, other):
        """
        Pipes the result of this step to other.


        Arguments:
            other: A different step object whose class subclasses this one.

        Returns:
            :py:class:`ibex.sklearn.pipeline.Pipeline`
        """

        from ._pipeline import _Pipeline

        if isinstance(other, _Pipeline):
            others = [operator.itemgetter(1)(e) for e in other.steps]
        else:
            others = [other]
        combined = [self] + others

        return _Pipeline(_make_pipeline_steps(combined))

    def __ror__(self, other):
        """

        Returns:
            :py:class:`ibex.sklearn.pipeline.Pipeline`
        """

        from ._pipeline import _Pipeline

        if isinstance(other, _Pipeline):
            others = [operator.itemgetter(1)(e) for e in other.steps]
        else:
            others = [other]
        combined = others + [self]

        return _Pipeline(_make_pipeline_steps(combined))

    def __add__(self, other):
        """

        Returns:
            :py:class:`ibex.sklearn.pipeline.FeatureUnion`
        """

        from ._pipeline import _FeatureUnion

        if isinstance(self, _FeatureUnion):
            self_features = [operator.itemgetter(1)(e) for e in self.transformer_list]
        else:
            self_features = [self]

        if isinstance(other, _FeatureUnion):
            other_features = [operator.itemgetter(1)(e) for e in other.transformer_list]
        else:
            other_features = [other]

        combined = self_features + other_features

        return _FeatureUnion(_make_pipeline_steps(combined))
