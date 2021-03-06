from __future__ import absolute_import


import inspect
import types
import re

import six
import numpy as np
import pandas as pd

from ._utils import verify_x_type, verify_y_type
from ._utils import update_method_wrapper, update_class_wrapper
from ._utils import wrapped_fn_names
from ._utils import get_wrapped_y
from ._base import InOpChecker


__all__ = []


_in_ops = InOpChecker(__file__)


def _inject_to_str_repr(rpr):
    _repr_re = re.compile(r'<(.+) at (0x[^>]+)>')
    m = _repr_re.match(rpr)
    if m is not None:
        groups = m.groups()
        return 'Adapter[' + groups[0] + '] at ' + groups[1]

    _sig_re = re.compile(r'([^\(]+)\(([^\)]+)\)')
    m = _sig_re.match(rpr)
    if m is not None:
        groups = m.groups()
        return 'Adapter[' + groups[0] + '](' + groups[1] + ')'

    return 'Adapter[' + repr + ']'


def _from_pickle(
        est,
        params,
        extra_methods,
        extra_attribs,
    post_op):
    cls = frame_ex(est, extra_methods, extra_attribs, post_op)
    est = cls(**params)
    return est


def make_adapter(
        est,
        extra_methods,
        extra_attribs,
    post_op):
    from ._base import FrameMixin

    extra_attribs_d = {fn.__name__: fn for fn in extra_attribs}
    extra_methods_d = {fn.__name__: fn for fn in extra_methods}

    class _Adapter(est, FrameMixin):
        def __repr__(self):
            ret = _inject_to_str_repr(est.__repr__(self))
            if '__repr__ ' in extra_attribs_d:
                return extra_attribs_d['__repr'](self, ret)
            return ret

        def __str__(self):
            ret = self.__repr__()
            if '__str__ ' in extra_attribs_d:
                return extra_attribs_d['__str__'](self, ret)
            return ret

        def aic(self, X, *args, **kwargs):
            return self.__adapter_run(
                super(_Adapter, self).aic,
                'aic',
                X,
                *args,
                **kwargs)

        def apply(self, X, *args, **kwargs):
            return self.__adapter_run(
                super(_Adapter, self).apply,
                'apply',
                X,
                *args,
                **kwargs)

        def decision_function(self, X, *args, **kwargs):
            return self.__adapter_run(
                super(_Adapter, self).decision_function,
                'decision_function',
                X,
                *args,
                **kwargs)

        def bic(self, X, *args, **kwargs):
            return self.__adapter_run(
                super(_Adapter, self).bic,
                'bic',
                X,
                *args,
                **kwargs)

        def fit(self, X, *args, **kwargs):
            return self.__adapter_run(
                super(_Adapter, self).fit,
                'fit',
                X,
                *args,
                **kwargs)

        def fit_predict(self, X, *args, **kwargs):
            return self.__adapter_run(
                super(_Adapter, self).fit_predict,
                'fit_predict',
                X,
                *args,
                **kwargs)

        def fit_transform(self, X, *args, **kwargs):
            return self.__adapter_run(
                super(_Adapter, self).fit_transform,
                'fit_transform',
                X,
                *args,
                **kwargs)

        def inverse_transform(self, X, *args, **kwargs):
            return self.__adapter_run(
                super(_Adapter, self).inverse_transform,
                'inverse_transform',
                X,
                *args,
                **kwargs)

        def kneighbors(self, X, *args, **kwargs):
            return self.__adapter_run(
                super(_Adapter, self).kneighbors,
                'kneighbors',
                X,
                *args,
                **kwargs)

        def partial_fit(self, X, *args, **kwargs):
            return self.__adapter_run(
                super(_Adapter, self).partial_fit,
                'partial_fit',
                X,
                *args,
                **kwargs)

        def perplexity(self, X, *args, **kwargs):
            return self.__adapter_run(
                super(_Adapter, self).perplexity,
                'perplexity',
                X,
                *args,
                **kwargs)

        def predict(self, X, *args, **kwargs):
            return self.__adapter_run(
                super(_Adapter, self).predict,
                'predict',
                X,
                *args,
                **kwargs)

        def predict_log_proba(self, X, *args, **kwargs):
            res = self.__adapter_run(
                super(_Adapter, self).predict_log_proba,
                'predict_log_proba',
                X,
                *args,
                **kwargs)
            if self not in _in_ops and hasattr(self, 'classes_'):
                res.columns = self.classes_
            return res

        def predict_proba(self, X, *args, **kwargs):
            res = self.__adapter_run(
                super(_Adapter, self).predict_proba,
                'predict_proba',
                X,
                *args,
                **kwargs)
            if self not in _in_ops and hasattr(self, 'classes_'):
                res.columns = self.classes_
            return res

        def radius_neighbors(self, X, *args, **kwargs):
            return self.__adapter_run(
                super(_Adapter, self).radius_neighbors,
                'radius_neighbors',
                X,
                *args,
                **kwargs)

        def sample_y(self, X, *args, **kwargs):
            return self.__adapter_run(
                super(_Adapter, self).sample_y,
                'sample_y',
                X,
                *args,
                **kwargs)

        def score_samples(self, X, *args, **kwargs): return self.__adapter_run(
                super(_Adapter, self).score_samples,
                'score_samples',
                X,
                *args,
                **kwargs)

        def staged_decision_function(self, X, *args, **kwargs):
            return self.__adapter_run(
                super(_Adapter, self).staged_decision_function,
                'staged_decision_function',
                X,
                *args,
                **kwargs)

        def staged_predict(self, X, *args, **kwargs):
            return self.__adapter_run(
                super(_Adapter, self).staged_predict,
                'staged_predict',
                X, *args,
                **kwargs)

        def staged_predict_proba(self, X, *args, **kwargs):
            return self.__adapter_run(
                super(_Adapter, self).staged_predict_proba,
                'staged_predict_proba',
                X,
                *args,
                **kwargs)

        def score(self, X, *args, **kwargs):
            return self.__adapter_run(
                super(_Adapter, self).score,
                'score',
                X,
                *args,
                **kwargs)

        def transform(self, X, *args, **kwargs):
            return self.__adapter_run(
                super(_Adapter, self).transform,
                'transform',
                X,
                *args,
                **kwargs)

        def __adapter_run(self, fn, name, X, *args, **kwargs):
            if self in _in_ops:
                return fn(X, *args, **kwargs)

            if not isinstance(X, pd.DataFrame):
                verify_x_type(X)

            # Tmp Ami - why not in function adapter? where are uts?
            if name.startswith('fit'):
                self.x_columns = X.columns

            y = get_wrapped_y(name, args)
            verify_y_type(y)
            # Tmp Ami - should go in utils
            if y is not None and not X.index.equals(y.index):
                raise ValueError('Indexes do not match')
            if y is not None:
                if name.startswith('fit'):
                    self.y_columns = y.columns if isinstance(y, pd.DataFrame) else None

            inv = name == 'inverse_transform'

            _in_ops.add(self)
            try:
                res = fn(self.__x(inv, X), *args, **kwargs)
            finally:
                _in_ops.remove(self)

            ret = self.__adapter_process_wrapped_call_res(inv, X, res)

            if name in extra_methods_d:
                ret = extra_methods_d[name](self, ret)

            return ret

        # Tmp Ami - should be in base?
        def __x(self, inv, X):
            return X[self.x_columns] if not inv else X

        def __adapter_process_wrapped_call_res(self, inv, X, res):
            if inv:
                return pd.DataFrame(res, index=X.index, columns=self.x_columns)

            X = X[self.x_columns]

            if isinstance(res, np.ndarray):
                if len(res.shape) == 1:
                    return pd.Series(res, index=X.index)

                if len(res.shape) == 2:
                    if len(X.columns) == res.shape[1]:
                        columns = X.columns
                    else:
                        columns = [' ' for _ in range(res.shape[1])]
                    return pd.DataFrame(res, index=X.index, columns=columns)

            if isinstance(res, types.GeneratorType):
                return (self.__adapter_process_wrapped_call_res(False, X, r) for r in res)

            return res

        def __getattribute__(self, name):
            base_ret = est.__getattribute__(self, name)
            if self not in _in_ops and name in extra_attribs_d:
                return extra_attribs_d[name](self, base_ret)
            return base_ret

        def __reduce__(self):
            if not self.__module__.startswith('ibex'):
                raise TypeError('Cannot serialize a subclass of this type; please use composition instead')
            return (_from_pickle, (est, self.get_params(deep=True), extra_methods, extra_attribs, post_op))

    if post_op is not None:
        post_op(_Adapter)

    return _Adapter


def frame_ex(est, extra_methods=(), extra_attribs=(), post_op=None):
    from ._base import FrameMixin

    if isinstance(est, FrameMixin):
        return est

    if not inspect.isclass(est):
        params = est.get_params()
        f = frame(type(est))(**params)
        return f

    _Adapter = make_adapter(est, extra_methods, extra_attribs, post_op)

    update_class_wrapper(_Adapter, est)

    _Adapter.__name__ = est.__name__

    for name, func in vars(_Adapter).items():
        if name.startswith('_'):
            continue

        parfunc = getattr(est, name, None)
        if parfunc and getattr(parfunc, '__doc__', None):
            func.__doc__ = parfunc.__doc__

    for wrap in wrapped_fn_names:
        if not hasattr(est, wrap) and hasattr(_Adapter, wrap):
            delattr(_Adapter, wrap)
        elif six.callable(getattr(_Adapter, wrap)):
            try:
                update_method_wrapper(_Adapter, est, wrap)
            except AttributeError:
                pass

    return _Adapter


def frame(est):
    """
    Arguments:
        est: either an estimator class or an estimator object. The class (or class of the
            object) should subclass :py:class:`sklearn.base.BaseEstimator`.

    Returns:
        If ``est`` is a class, returns a class; if ``est`` is an object,
            returns an object. Note that the result will subclass ``est``
            and :py:class:`ibex.FrameMixin`

    Example:

        >>> from sklearn import linear_model
        >>> from ibex import frame

        We can use ``frame`` to adapt an object:

        >>> prd = frame(linear_model.LinearRegression())
        >>> prd
        Adapter[LinearRegression](copy_X=True, fit_intercept=True, n_jobs=1, normalize=False)

        We can use ``frame`` to adapt a class:

        >>> PdLinearRegression = frame(linear_model.LinearRegression)
        >>> PdLinearRegression()
        Adapter[LinearRegression](copy_X=True, fit_intercept=True, n_jobs=1, normalize=False)

        >>> PdLinearRegression(fit_intercept=False)
        Adapter[LinearRegression](copy_X=True, fit_intercept=False, n_jobs=1, normalize=False)
    """
    return frame_ex(est, extra_methods=(), extra_attribs=())


__all__ += ['frame']
