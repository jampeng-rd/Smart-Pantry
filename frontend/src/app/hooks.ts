import { useDispatch, useSelector } from "react-redux";

import type { AppDispatch, RootState } from "./store";

/** 提供具型別的 dispatch。 */
export const useAppDispatch = useDispatch.withTypes<AppDispatch>();
/** 提供具型別的 selector。 */
export const useAppSelector = useSelector.withTypes<RootState>();
