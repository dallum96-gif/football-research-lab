"""Projection Lab workspace built around the existing Poisson model."""

import streamlit as st

from gui.projection_lab_v2 import render_projection_lab as _render_projection_lab


def render_projection_lab():
    _render_projection_lab()
