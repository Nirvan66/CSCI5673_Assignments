struct intpair {
        int a;
        int b;
};

program ADD_PROG {
        version ADD_VERS {
                intpair ADD() = 1;
        } = 1;
} = 0x23451111;