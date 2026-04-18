export type ByStrategy = 'XPATH' | 'ID' | 'CLASS' | 'CSS_SELECTOR';
export type IfListStrategy = 'all' | 'first' | 'last' | 'even' | 'odd' | 'number' | 'interval';

export interface Locator {
  attribute: string;
  by: ByStrategy;
  selector: string;
  strategy_for_multiple_selectors: string;
  if_list: IfListStrategy | string;
  mandatory: boolean;
  text_to_be_present_in_element: string;
  event: boolean | null;
  timeout_for_event: string;
  timeout: number;
  locator_description: string;
}

export interface LocatorsData {
  supplier_prefix: string;
  locators: Record<string, Locator>;
}