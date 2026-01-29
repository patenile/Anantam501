
import React from 'react';
import { render, screen } from '@testing-library/react';
import App from './App';
import { describe, it, expect } from 'vitest';
import '@testing-library/jest-dom';

describe('App', () => {
  it('renders the main heading', () => {
    render(<App />);
    expect(screen.getByRole('heading')).toBeInTheDocument();
  });
});
