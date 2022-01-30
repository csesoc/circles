export const courseOptionsActions = (action, payload) => {
    switch (action) {
        case 'LOAD_PREV_STATE': 
            return {
                type: 'LOAD_PREV_STATE', 
                payload: payload,
            }
        case 'SET_CORE_COURSES': 
            return {
                type: 'SET_CORE_COURSES',
                payload: payload
            }
        case 'SET_ELECTIVE_COURSES': 
            return {
                type: 'SET_ELECTIVE_COURSES',
                payload: payload
            }
        case 'SET_GENED_COURSES': 
            return {
                type: 'SET_GENED_COURSES',
                payload: payload
            }
        case 'APPEND_COURSE':
            return {
                type: 'APPEND_COURSE',
                payload: payload
            }
        default:
            return null;
    }

}