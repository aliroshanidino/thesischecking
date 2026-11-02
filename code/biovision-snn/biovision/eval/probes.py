"""Linear SVM probe on spiking features (CLAUDE.md 1.3.2: an evaluation probe in Phases 0–1, not part of the
spiking network).

* ``kind="ovr"`` (default): one-versus-rest linear SVM with exactly the objective of ``LinearSVC`` (squared hinge
  loss, L2 penalty on the weights and on the intercept), solved in the primal by L-BFGS with torch. liblinear's
  dual solver needed up to tens of minutes on our nearly separable, standardised high-dimensional features
  (D21); the objective is strictly convex, so both solvers target the same unique solution.
* ``kind="liblinear"``: sklearn ``LinearSVC`` itself; ``kind="ovo"``: ``SVC(kernel="linear")`` (one-versus-one, as
  Kheradpisheh et al. 2016).
* ``select_C``: the penalty ``C`` chosen by cross-validation INSIDE the training set (grouped by object instance for
  ETH-80, so views of one object never sit on both sides), instead of a grid search on the test set.
"""

from __future__ import annotations

import numpy as np
from sklearn.metrics import confusion_matrix
from sklearn.svm import SVC, LinearSVC

C_GRID = (0.0001, 0.0003, 0.001, 0.003, 0.01, 0.03, 0.1, 0.3, 1.0, 3.0)


class TorchLinearSVC:
    """One-versus-rest linear SVM: per class ``0.5 (|w|^2 + b^2) + C sum_i max(0, 1 - y_i (w.x_i + b))^2``."""

    def __init__(self, C: float = 1.0, max_iter: int = 1000, tol: float = 1e-6):
        self.C, self.max_iter, self.tol = C, max_iter, tol

    def fit(self, X, y):
        import torch
        X = torch.as_tensor(np.asarray(X, dtype=np.float32))
        y = np.asarray(y)
        self.classes_ = np.unique(y)
        Y = torch.as_tensor(np.where(y[:, None] == self.classes_[None, :], 1.0, -1.0), dtype=torch.float32)
        dt = torch.float64 if X.numel() <= 2e7 else torch.float32  # RAM: MNIST is 60k x 2500 features
        Xb = torch.cat([X, torch.ones(len(X), 1)], 1).to(dt)       # intercept as an extra (penalised) feature
        Y = Y.to(dt)
        del X
        W = torch.zeros(Xb.shape[1], Y.shape[1], dtype=dt, requires_grad=True)
        opt = torch.optim.LBFGS([W], lr=1, max_iter=self.max_iter, tolerance_grad=self.tol,
                                tolerance_change=1e-12, history_size=20, line_search_fn="strong_wolfe")

        def closure():
            opt.zero_grad()
            m = (1 - Y * (Xb @ W)).clamp_min(0)
            loss = 0.5 * (W * W).sum() + self.C * (m * m).sum()
            loss.backward()
            return loss
        opt.step(closure)
        self.coef_ = W.detach()[:-1].t().double().numpy()
        self.intercept_ = W.detach()[-1].double().numpy()
        return self

    def decision_function(self, X):
        return np.asarray(X, dtype=np.float64) @ self.coef_.T + self.intercept_

    def predict(self, X):
        return self.classes_[self.decision_function(X).argmax(1)]


def make_svm(C: float, seed: int = 0, kind: str = "ovr"):
    if kind == "ovo":
        return SVC(kernel="linear", C=C, random_state=seed)
    if kind == "liblinear":
        return LinearSVC(C=C, max_iter=50000, random_state=seed)
    return TorchLinearSVC(C=C)


def svm_probe(train_x: np.ndarray, train_y, test_x: np.ndarray, test_y, C: float, seed: int = 0,
              kind: str = "ovr") -> dict:
    clf = make_svm(C, seed, kind)
    clf.fit(train_x, train_y)
    pred = clf.predict(test_x)
    return {
        "train_acc": float((clf.predict(train_x) == np.asarray(train_y)).mean()),
        "test_acc": float((pred == np.asarray(test_y)).mean()),
        "confusion": confusion_matrix(test_y, pred).tolist(),
        "pred": pred.tolist(),
    }


def select_C(train_x: np.ndarray, train_y, groups=None, grid=C_GRID, folds: int = 5, seed: int = 0,
             kind: str = "ovr", max_n: int = 8000) -> tuple[float, dict]:
    """Best ``C`` by (grouped) k-fold cross-validation on the training features; returns ``(C, {C: cv_acc})``."""
    from sklearn.model_selection import StratifiedGroupKFold, StratifiedKFold
    y = np.asarray(train_y)
    idx = np.arange(len(y))
    if len(idx) > max_n:  # large sets (MNIST): a random stratified subsample is enough to rank C values
        rng = np.random.default_rng(seed)
        idx = np.sort(rng.choice(idx, max_n, replace=False))
    X, y = train_x[idx], y[idx]
    if groups is not None:
        g = np.asarray(groups)[idx]
        splits = list(StratifiedGroupKFold(n_splits=min(folds, len(np.unique(g)))).split(X, y, g))
    else:
        splits = list(StratifiedKFold(n_splits=folds, shuffle=True, random_state=seed).split(X, y))
    scores = {}
    for C in grid:
        acc = [float((make_svm(C, seed, kind).fit(X[a], y[a]).predict(X[b]) == y[b]).mean()) for a, b in splits]
        scores[C] = float(np.mean(acc))
    best = max(scores, key=lambda c: (scores[c], -c))  # ties: the smaller (more regularised) C
    return best, scores
