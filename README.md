# Jannik Tode Bachelors Project

## Summary

This is my  project for my bachelors thesis.
The code for the testbeds is divided into the folders `dcube` and `testbed` (being Kiel). 
This is due to the fact that in order to evaluate the testbed results, gpio tracing is needed. Therefore Kiel has to `gpio_pin_toggle(la_dev, PIN);` after sending/receiving.
The Throughput experiments have an extra folder, since latency is not evaluated here.

## Code
The different parameters are changed by adjusting the following parts of the code:
### Number of senders
#### DCube
The number of senders can be changed by adjusting the uuids in `main.c`:

```C
static uint8_t cmp_uuid[4][16] = {{0xec, 0xb4, 0x53, 0x12, 0x16, 0x7c, 0x7c, 0x75, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00}, //ID: 108
				  {0xe5, 0x54, 0x39, 0x6d, 0xf1, 0x11, 0xde, 0x36, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00}, //ID: 200
				  {0xe5, 0x94, 0xe2, 0x23, 0xc1, 0x3e, 0x54, 0x5b, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00}, //ID: 212
				  {0x9d, 0x97, 0x9f, 0xbc, 0x74, 0x24, 0xd2, 0xd8, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00}};//ID: 225
```

#### Kiel
The number of senders can be changed by adjusting the following code:

```C
if(uuid_in_list(dev_uuid, cmp_uuid)){
    node_id = 5;
    helper = true;
}
/*else if(uuid_in_list(dev_uuid, cmp_uuid2)){
    node_id = 2;
    helper = false;
}
else if(uuid_in_list(dev_uuid, cmp_uuid8)){
    node_id = 8;
    helper = false;
}
else if(uuid_in_list(dev_uuid, cmp_uuid19)){
    node_id = 19;
    helper = false;
}*/
```

This difference in the code is not really significant and doesnt really have a reason.

### Packet Size
The packet size is changed by adjusting the code within the `static int gen_onoff_send(bool val)` function:

```C
int payload_size = (8+16+8+64+32+16+8)/8;
uint64_t extra_payload = 0;

BT_MESH_MODEL_BUF_DEFINE(buf, OP_ONOFF_SET_UNACK, payload_size);
bt_mesh_model_msg_init(&buf, OP_ONOFF_SET_UNACK);
net_buf_simple_add_u8(&buf, val);
net_buf_simple_add_le16(&buf, tid++);
net_buf_simple_add_u8(&buf, node_id);

//extra payloads
net_buf_simple_add_le64(&buf, extra_payload);
net_buf_simple_add_le32(&buf, (uint32_t) extra_payload);
net_buf_simple_add_le16(&buf, (uint16_t)extra_payload);
net_buf_simple_add_u8(&buf, (uint8_t)extra_payload);
```

You can use e.g. `net_buf_simple_add_le64` to add 64 Bits of data. The different sizes used for this thesis are listed above. 
For adjusting the payload size, one must also change `int payload_size` to match the total payload size.

### Time To Live

To change the time to live, the configuration setting for time to live must be changed within `prj.conf`: 
```
CONFIG_BT_MESH_DEFAULT_TTL=7
```

### Transmit Power

To change the transmit, one of the following settings must be changed within `prj.conf`: 
```
CONFIG_BT_CTLR_TX_PWR_0=y
CONFIG_BT_CTLR_TX_PWR_MINUS_4=y
CONFIG_BT_CTLR_TX_PWR_PLUS_4=y
```

### Periodicity

To change the periodicity of sent packets, x must be changed to the seconds after which should be sent must be changed in `void main` within `main.c`: 
```C
//Initiate Timer
k_timer_init(&my_timer, send, NULL);

//timer expires once per second
k_timer_start(&my_timer, K_SECONDS(x), K_SECONDS(x));
```

Therefore x=0.5 equals sending every half second which results in 2 packets per second.

### Retransmissions

To change the amount of retransmissions, the following setting must be changed within `prj.conf`: 
```
CONFIG_BT_MESH_RELAY_RETRANSMIT_COUNT=2
```
Note that the total amount of transmissions is always one higher, than the setting, since the retransmissions do not include the inital sending of the packet.

### Channels

In order to adjust the channels, there is a standard configuration used with change of the bluetooth driver files within zephyr.
