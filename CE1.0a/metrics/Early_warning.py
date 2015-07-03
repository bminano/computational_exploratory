#!/usr/bin/python

import numpy as np

def early_warning_difference(time_series_ref, time_series_comp, change_values, warning_values, histogram_limit=50):
    '''Early warning differencial

    Input:
        time_series_ref     Referential time series
        time_series_comp    Time series comparison
        change_values       The values to consider an status change
        warning_values      The values to consider a warning 
        histogram_limit     maximum difference to consider. Greater differences are casted to this limit

        returns             Differential from early warnings array

    '''
    print warning_values
    assert len(warning_values) == 2, "One lower and one upper value must be set for the warning states"
    assert len(change_values) == 2, "One lower and one upper value must be set for the changing states"

    lower_warning = warning_values[0]
    upper_warning = warning_values[1]
    lower_change = change_values[0]
    upper_change = change_values[1]

    state = True
    warning_state_acc_comp = 0
    warning_state_acc_ref = 0
    last_time_t_comp = -1
    last_time_t_ref = -1

    ew_dif = []
    for t in xrange(len(time_series_ref)):
        print t
        '''Update signals'''
        if time_series_comp[t] < lower_warning and (state or warning_state_acc_comp >= 1):
            if warning_state_acc_comp == -1:
                last_time_t_comp = t
            warning_state_acc_comp -= 1
            '''False previous early warning, so reset'''
            if warning_state_acc_comp == 1:
                last_time_t_comp = -1
        else:
            if time_series_comp[t] > upper_warning and (not state or warning_state_acc_comp <= -1):
                if warning_state_acc_comp == 1:
                    last_time_t_comp = t
                warning_state_acc_comp += 1
                '''False previous early warning, so reset'''
                if warning_state_acc_comp == -1:
                    last_time_t_comp = -1
        if time_series_ref[t] < lower_warning and (state or warning_state_acc_ref >= 1):
            if warning_state_acc_ref == -1:
                last_time_t_ref = t
            warning_state_acc_ref -= 1
            '''False previous early warning, so reset'''
            if warning_state_acc_ref == 1:
                last_time_t_ref = -1
        else:
            if time_series_ref[t] > upper_warning and (not state or warning_state_acc_ref <= -1):
                if warning_state_acc_ref == 1:
                    last_time_t_ref = t
                warning_state_acc_ref += 1
                '''False previous early warning, so reset'''
                if warning_state_acc_ref == -1:
                    last_time_t_ref = -1

        '''State change'''
        stateChange = False
        if (state and time_series_ref[t] < lower_change) or (not state and time_series_ref[t] > upper_change):
            if (last_time_t_ref == -1):
                last_time_t_ref = t
            if (last_time_t_comp == -1):
                last_time_t_comp = t
            dt = last_time_t_ref - last_time_t_comp
            last_time_t_ref = -1
            last_time_t_comp = -1
            warning_state_acc_ref = 0
            warning_state_acc_comp = 0
            state = not state
            ew_dif.append(dt)
            stateChange = True

    return np.asarray(ew_dif)

def early_warning_flips(time_series, change_values):
    '''Early warning differencial

    Input:
        time_series_ref     Referential time series
        time_series_comp    Time series comparison
        change_values       The values to consider an status change
        warning_values      The values to consider a warning 
        histogram_limit     maximum difference to consider. Greater differences are casted to this limit

        returns             Differential from early warnings array

    '''
    assert len(change_values) == 2, "One lower and one upper value must be set for the changing states"

    lower_change = change_values[0]
    upper_change = change_values[1]

    state = True
    last_time = -1

    ew_dif = []
    for t in xrange(len(time_series)):
        print t

        '''State change'''
        stateChange = False
        if (state and time_series[t] < lower_change) or (not state and time_series[t] > upper_change):
            if (last_time == -1):
                last_time = t
            else:
                dt = t - last_time
                last_time = t
                state = not state
                ew_dif.append(dt)
            stateChange = True

    return np.asarray(ew_dif)
