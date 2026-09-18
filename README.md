# Fireflies collector to run at UC

[![Build Fireflies Logstash dockerhub image](https://github.com/ATLAS-Analytics/uc_ls_collectors/actions/workflows/fireflies.yaml/badge.svg)](https://github.com/ATLAS-Analytics/uc_ls_collectors/actions/workflows/fireflies.yaml)

Consumes the ESnet Stardust firefly stream from Kafka and indexes it into the
`fireflies_write` Elasticsearch alias on `atlas-kibana.mwt2.org`. There is no filter
stage - documents are indexed as they arrive on the topic.

## Configuration

All connection details come from environment variables. Everything except the two
passwords has a working default baked into [configs/fireflies.conf](configs/fireflies.conf).

| Variable | Default | Notes |
| --- | --- | --- |
| `KAFKA_PWD` | *(none - required)* | Kafka SASL password. Must come from a secret. |
| `LOGSTASH_PWD` | *(none - required)* | Elasticsearch password for `uc_logstash_indexer`. |
| `KAFKA_BOOTSTRAP_SERVERS` | `message-exchange.es.net:9095` | |
| `KAFKA_TOPIC` | `stardust_firefly` | |
| `KAFKA_GROUP_ID` | `firefly-cern-uccollect-consumer-01` | Consumer group. The broker ACL only grants this one - any other group is rejected with `GroupAuthorizationException`. |
| `KAFKA_CLIENT_ID` | `uc-ls-fireflies` | |
| `KAFKA_USERNAME` | `kafka-cern-user-uccollect-external-community` | |
| `KAFKA_SECURITY_PROTOCOL` | `SASL_SSL` | |
| `KAFKA_SASL_MECHANISM` | `SCRAM-SHA-512` | |
| `KAFKA_AUTO_OFFSET_RESET` | `latest` | Set to `earliest` to backfill from the retained log. |
| `KAFKA_CONSUMER_THREADS` | `1` | Do not exceed the topic's partition count. |
| `KAFKA_TRUSTSTORE` | `/usr/share/logstash/certs/kafka-ca.pem` | ESnet cluster CA - see below. |
| `KAFKA_TRUSTSTORE_TYPE` | `PEM` | |
| `KAFKA_SSL_ENDPOINT_ID_ALGO` | *(empty)* | See below. |

### TLS against the ESnet broker

`message-exchange.es.net:9095` is a Strimzi cluster, which means two things the
defaults do not handle:

* Its certificate is issued by a **self-signed `io.strimzi` cluster CA**, which does not
  chain to the JDK default truststore. The CA has to be mounted at `KAFKA_TRUSTSTORE`,
  otherwise the handshake fails with `PKIX path building failed`. The CA currently in use
  is `O=io.strimzi, CN=cluster-ca v0`, valid until **2027-07-23**; it will need replacing
  when ESnet rotates it.
* The broker certificate lists only the in-cluster service names and broker IPs as SANs -
  there is **no SAN for `message-exchange.es.net`** - so hostname verification cannot
  succeed against the public name, and `KAFKA_SSL_ENDPOINT_ID_ALGO` is left empty.
  Trust is still pinned to the cluster CA above, so this is narrower than trusting a
  public CA set. Set it to `https` if ESnet ever adds the SAN.

### Deployment

Mount the CA and both passwords, alongside the usual `LOGSTASH_PWD` handling used by
the other collectors in this repository:

```yaml
env:
  - name: LOGSTASH_PWD
    valueFrom:
      secretKeyRef:
        name: logstash-pwd
        key: password
  - name: KAFKA_PWD
    valueFrom:
      secretKeyRef:
        name: fireflies-kafka
        key: password
volumeMounts:
  - name: kafka-ca
    mountPath: /usr/share/logstash/certs
    readOnly: true
volumes:
  - name: kafka-ca
    configMap:
      name: fireflies-kafka-ca   # key: kafka-ca.pem
```
