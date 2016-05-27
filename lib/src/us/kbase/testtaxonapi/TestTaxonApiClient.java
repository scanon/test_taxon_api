package us.kbase.testtaxonapi;

import com.fasterxml.jackson.core.type.TypeReference;
import java.io.File;
import java.io.IOException;
import java.net.URL;
import java.util.ArrayList;
import java.util.List;
import us.kbase.auth.AuthToken;
import us.kbase.common.service.JsonClientCaller;
import us.kbase.common.service.JsonClientException;
import us.kbase.common.service.RpcContext;
import us.kbase.common.service.UnauthorizedException;

/**
 * <p>Original spec-file module name: test_taxon_api</p>
 * <pre>
 * A KBase module: test_taxon_api
 * </pre>
 */
public class TestTaxonApiClient {
    private JsonClientCaller caller;


    /** Constructs a client with a custom URL and no user credentials.
     * @param url the URL of the service.
     */
    public TestTaxonApiClient(URL url) {
        caller = new JsonClientCaller(url);
    }
    /** Constructs a client with a custom URL.
     * @param url the URL of the service.
     * @param token the user's authorization token.
     * @throws UnauthorizedException if the token is not valid.
     * @throws IOException if an IOException occurs when checking the token's
     * validity.
     */
    public TestTaxonApiClient(URL url, AuthToken token) throws UnauthorizedException, IOException {
        caller = new JsonClientCaller(url, token);
    }

    /** Constructs a client with a custom URL.
     * @param url the URL of the service.
     * @param user the user name.
     * @param password the password for the user name.
     * @throws UnauthorizedException if the credentials are not valid.
     * @throws IOException if an IOException occurs when checking the user's
     * credentials.
     */
    public TestTaxonApiClient(URL url, String user, String password) throws UnauthorizedException, IOException {
        caller = new JsonClientCaller(url, user, password);
    }

    /** Get the token this client uses to communicate with the server.
     * @return the authorization token.
     */
    public AuthToken getToken() {
        return caller.getToken();
    }

    /** Get the URL of the service with which this client communicates.
     * @return the service URL.
     */
    public URL getURL() {
        return caller.getURL();
    }

    /** Set the timeout between establishing a connection to a server and
     * receiving a response. A value of zero or null implies no timeout.
     * @param milliseconds the milliseconds to wait before timing out when
     * attempting to read from a server.
     */
    public void setConnectionReadTimeOut(Integer milliseconds) {
        this.caller.setConnectionReadTimeOut(milliseconds);
    }

    /** Check if this client allows insecure http (vs https) connections.
     * @return true if insecure connections are allowed.
     */
    public boolean isInsecureHttpConnectionAllowed() {
        return caller.isInsecureHttpConnectionAllowed();
    }

    /** Deprecated. Use isInsecureHttpConnectionAllowed().
     * @deprecated
     */
    public boolean isAuthAllowedForHttp() {
        return caller.isAuthAllowedForHttp();
    }

    /** Set whether insecure http (vs https) connections should be allowed by
     * this client.
     * @param allowed true to allow insecure connections. Default false
     */
    public void setIsInsecureHttpConnectionAllowed(boolean allowed) {
        caller.setInsecureHttpConnectionAllowed(allowed);
    }

    /** Deprecated. Use setIsInsecureHttpConnectionAllowed().
     * @deprecated
     */
    public void setAuthAllowedForHttp(boolean isAuthAllowedForHttp) {
        caller.setAuthAllowedForHttp(isAuthAllowedForHttp);
    }

    /** Set whether all SSL certificates, including self-signed certificates,
     * should be trusted.
     * @param trustAll true to trust all certificates. Default false.
     */
    public void setAllSSLCertificatesTrusted(final boolean trustAll) {
        caller.setAllSSLCertificatesTrusted(trustAll);
    }
    
    /** Check if this client trusts all SSL certificates, including
     * self-signed certificates.
     * @return true if all certificates are trusted.
     */
    public boolean isAllSSLCertificatesTrusted() {
        return caller.isAllSSLCertificatesTrusted();
    }
    /** Sets streaming mode on. In this case, the data will be streamed to
     * the server in chunks as it is read from disk rather than buffered in
     * memory. Many servers are not compatible with this feature.
     * @param streamRequest true to set streaming mode on, false otherwise.
     */
    public void setStreamingModeOn(boolean streamRequest) {
        caller.setStreamingModeOn(streamRequest);
    }

    /** Returns true if streaming mode is on.
     * @return true if streaming mode is on.
     */
    public boolean isStreamingModeOn() {
        return caller.isStreamingModeOn();
    }

    public void _setFileForNextRpcResponse(File f) {
        caller.setFileForNextRpcResponse(f);
    }

    /**
     * <p>Original spec-file function name: get_parent</p>
     * <pre>
     * *
     * * Retrieve parent Taxon.
     * *
     * * @return Reference to parent Taxon.
     * </pre>
     * @param   ref   instance of original type "ObjectReference" (Insert your typespec information here.)
     * @return   instance of original type "ObjectReference" (Insert your typespec information here.)
     * @throws IOException if an IO exception occurs
     * @throws JsonClientException if a JSON RPC exception occurs
     */
    public String getParent(String ref, RpcContext... jsonRpcContext) throws IOException, JsonClientException {
        List<Object> args = new ArrayList<Object>();
        args.add(ref);
        TypeReference<List<String>> retType = new TypeReference<List<String>>() {};
        List<String> res = caller.jsonrpcCall("test_taxon_api.get_parent", args, retType, true, true, jsonRpcContext);
        return res.get(0);
    }

    /**
     * <p>Original spec-file function name: get_children</p>
     * <pre>
     * *
     * * Retrieve children Taxon.
     * *
     * * @return List of references to child Taxons.
     * </pre>
     * @param   ref   instance of original type "ObjectReference" (Insert your typespec information here.)
     * @return   instance of list of original type "ObjectReference" (Insert your typespec information here.)
     * @throws IOException if an IO exception occurs
     * @throws JsonClientException if a JSON RPC exception occurs
     */
    public List<String> getChildren(String ref, RpcContext... jsonRpcContext) throws IOException, JsonClientException {
        List<Object> args = new ArrayList<Object>();
        args.add(ref);
        TypeReference<List<List<String>>> retType = new TypeReference<List<List<String>>>() {};
        List<List<String>> res = caller.jsonrpcCall("test_taxon_api.get_children", args, retType, true, true, jsonRpcContext);
        return res.get(0);
    }

    /**
     * <p>Original spec-file function name: get_genome_annotations</p>
     * <pre>
     * *
     * funcdef GenomeAnnotation(s) that refer to this Taxon.
     * * If this is accessing a KBaseGenomes.Genome object, it will
     * * return an empty list (this information is not available).
     * *
     * * @return List of references to GenomeAnnotation objects.
     * </pre>
     * @param   ref   instance of original type "ObjectReference" (Insert your typespec information here.)
     * @return   instance of list of original type "ObjectReference" (Insert your typespec information here.)
     * @throws IOException if an IO exception occurs
     * @throws JsonClientException if a JSON RPC exception occurs
     */
    public List<String> getGenomeAnnotations(String ref, RpcContext... jsonRpcContext) throws IOException, JsonClientException {
        List<Object> args = new ArrayList<Object>();
        args.add(ref);
        TypeReference<List<List<String>>> retType = new TypeReference<List<List<String>>>() {};
        List<List<String>> res = caller.jsonrpcCall("test_taxon_api.get_genome_annotations", args, retType, true, true, jsonRpcContext);
        return res.get(0);
    }

    /**
     * <p>Original spec-file function name: get_scientific_lineage</p>
     * <pre>
     * *
     * * Retrieve the scientific lineage.
     * *
     * * @return Strings for each 'unit' of the lineage, ordered in
     * *   the usual way from Domain to Kingdom to Phylum, etc.
     * *
     * </pre>
     * @param   ref   instance of original type "ObjectReference" (Insert your typespec information here.)
     * @return   instance of list of String
     * @throws IOException if an IO exception occurs
     * @throws JsonClientException if a JSON RPC exception occurs
     */
    public List<String> getScientificLineage(String ref, RpcContext... jsonRpcContext) throws IOException, JsonClientException {
        List<Object> args = new ArrayList<Object>();
        args.add(ref);
        TypeReference<List<List<String>>> retType = new TypeReference<List<List<String>>>() {};
        List<List<String>> res = caller.jsonrpcCall("test_taxon_api.get_scientific_lineage", args, retType, true, true, jsonRpcContext);
        return res.get(0);
    }

    /**
     * <p>Original spec-file function name: get_scientific_name</p>
     * <pre>
     * *
     * * Retrieve the scientific name.
     * *
     * * @return The scientific name, e.g., "Escherichia Coli K12 str. MG1655"
     * </pre>
     * @param   ref   instance of original type "ObjectReference" (Insert your typespec information here.)
     * @return   instance of String
     * @throws IOException if an IO exception occurs
     * @throws JsonClientException if a JSON RPC exception occurs
     */
    public String getScientificName(String ref, RpcContext... jsonRpcContext) throws IOException, JsonClientException {
        List<Object> args = new ArrayList<Object>();
        args.add(ref);
        TypeReference<List<String>> retType = new TypeReference<List<String>>() {};
        List<String> res = caller.jsonrpcCall("test_taxon_api.get_scientific_name", args, retType, true, true, jsonRpcContext);
        return res.get(0);
    }

    /**
     * <p>Original spec-file function name: get_taxonomic_id</p>
     * <pre>
     * *
     * * Retrieve the NCBI taxonomic ID of this Taxon.
     * * For type KBaseGenomes.Genome, the ``source_id`` will be returned.
     * *
     * * @return Integer taxonomic ID.
     * </pre>
     * @param   ref   instance of original type "ObjectReference" (Insert your typespec information here.)
     * @return   instance of Long
     * @throws IOException if an IO exception occurs
     * @throws JsonClientException if a JSON RPC exception occurs
     */
    public Long getTaxonomicId(String ref, RpcContext... jsonRpcContext) throws IOException, JsonClientException {
        List<Object> args = new ArrayList<Object>();
        args.add(ref);
        TypeReference<List<Long>> retType = new TypeReference<List<Long>>() {};
        List<Long> res = caller.jsonrpcCall("test_taxon_api.get_taxonomic_id", args, retType, true, true, jsonRpcContext);
        return res.get(0);
    }

    /**
     * <p>Original spec-file function name: get_kingdom</p>
     * <pre>
     * *
     * * Retrieve the kingdom.
     * *
     * </pre>
     * @param   ref   instance of original type "ObjectReference" (Insert your typespec information here.)
     * @return   instance of String
     * @throws IOException if an IO exception occurs
     * @throws JsonClientException if a JSON RPC exception occurs
     */
    public String getKingdom(String ref, RpcContext... jsonRpcContext) throws IOException, JsonClientException {
        List<Object> args = new ArrayList<Object>();
        args.add(ref);
        TypeReference<List<String>> retType = new TypeReference<List<String>>() {};
        List<String> res = caller.jsonrpcCall("test_taxon_api.get_kingdom", args, retType, true, true, jsonRpcContext);
        return res.get(0);
    }

    /**
     * <p>Original spec-file function name: get_domain</p>
     * <pre>
     * *
     * * Retrieve the domain.
     * *
     * </pre>
     * @param   ref   instance of original type "ObjectReference" (Insert your typespec information here.)
     * @return   instance of String
     * @throws IOException if an IO exception occurs
     * @throws JsonClientException if a JSON RPC exception occurs
     */
    public String getDomain(String ref, RpcContext... jsonRpcContext) throws IOException, JsonClientException {
        List<Object> args = new ArrayList<Object>();
        args.add(ref);
        TypeReference<List<String>> retType = new TypeReference<List<String>>() {};
        List<String> res = caller.jsonrpcCall("test_taxon_api.get_domain", args, retType, true, true, jsonRpcContext);
        return res.get(0);
    }

    /**
     * <p>Original spec-file function name: get_genetic_code</p>
     * <pre>
     * *
     * * Retrieve the genetic code.
     * *
     * </pre>
     * @param   ref   instance of original type "ObjectReference" (Insert your typespec information here.)
     * @return   instance of Long
     * @throws IOException if an IO exception occurs
     * @throws JsonClientException if a JSON RPC exception occurs
     */
    public Long getGeneticCode(String ref, RpcContext... jsonRpcContext) throws IOException, JsonClientException {
        List<Object> args = new ArrayList<Object>();
        args.add(ref);
        TypeReference<List<Long>> retType = new TypeReference<List<Long>>() {};
        List<Long> res = caller.jsonrpcCall("test_taxon_api.get_genetic_code", args, retType, true, true, jsonRpcContext);
        return res.get(0);
    }

    /**
     * <p>Original spec-file function name: get_aliases</p>
     * <pre>
     * *
     * * Retrieve the aliases.
     * *
     * </pre>
     * @param   ref   instance of original type "ObjectReference" (Insert your typespec information here.)
     * @return   instance of list of String
     * @throws IOException if an IO exception occurs
     * @throws JsonClientException if a JSON RPC exception occurs
     */
    public List<String> getAliases(String ref, RpcContext... jsonRpcContext) throws IOException, JsonClientException {
        List<Object> args = new ArrayList<Object>();
        args.add(ref);
        TypeReference<List<List<String>>> retType = new TypeReference<List<List<String>>>() {};
        List<List<String>> res = caller.jsonrpcCall("test_taxon_api.get_aliases", args, retType, true, true, jsonRpcContext);
        return res.get(0);
    }

    /**
     * <p>Original spec-file function name: get_info</p>
     * <pre>
     * *
     * * Retrieve object info.
     * * @skip documentation
     * </pre>
     * @param   ref   instance of original type "ObjectReference" (Insert your typespec information here.)
     * @return   instance of type {@link us.kbase.testtaxonapi.ObjectInfo ObjectInfo}
     * @throws IOException if an IO exception occurs
     * @throws JsonClientException if a JSON RPC exception occurs
     */
    public ObjectInfo getInfo(String ref, RpcContext... jsonRpcContext) throws IOException, JsonClientException {
        List<Object> args = new ArrayList<Object>();
        args.add(ref);
        TypeReference<List<ObjectInfo>> retType = new TypeReference<List<ObjectInfo>>() {};
        List<ObjectInfo> res = caller.jsonrpcCall("test_taxon_api.get_info", args, retType, true, true, jsonRpcContext);
        return res.get(0);
    }

    /**
     * <p>Original spec-file function name: get_history</p>
     * <pre>
     * *
     * * Retrieve object history.
     * * @skip documentation
     * </pre>
     * @param   ref   instance of original type "ObjectReference" (Insert your typespec information here.)
     * @return   instance of original type "ObjectHistory" (* @skip documentation) &rarr; list of type {@link us.kbase.testtaxonapi.ObjectInfo ObjectInfo}
     * @throws IOException if an IO exception occurs
     * @throws JsonClientException if a JSON RPC exception occurs
     */
    public List<ObjectInfo> getHistory(String ref, RpcContext... jsonRpcContext) throws IOException, JsonClientException {
        List<Object> args = new ArrayList<Object>();
        args.add(ref);
        TypeReference<List<List<ObjectInfo>>> retType = new TypeReference<List<List<ObjectInfo>>>() {};
        List<List<ObjectInfo>> res = caller.jsonrpcCall("test_taxon_api.get_history", args, retType, true, true, jsonRpcContext);
        return res.get(0);
    }

    /**
     * <p>Original spec-file function name: get_provenance</p>
     * <pre>
     * *
     * * Retrieve object provenance.
     * * @skip documentation
     * </pre>
     * @param   ref   instance of original type "ObjectReference" (Insert your typespec information here.)
     * @return   instance of original type "ObjectProvenance" (* @skip documentation) &rarr; list of type {@link us.kbase.testtaxonapi.ObjectProvenanceAction ObjectProvenanceAction}
     * @throws IOException if an IO exception occurs
     * @throws JsonClientException if a JSON RPC exception occurs
     */
    public List<ObjectProvenanceAction> getProvenance(String ref, RpcContext... jsonRpcContext) throws IOException, JsonClientException {
        List<Object> args = new ArrayList<Object>();
        args.add(ref);
        TypeReference<List<List<ObjectProvenanceAction>>> retType = new TypeReference<List<List<ObjectProvenanceAction>>>() {};
        List<List<ObjectProvenanceAction>> res = caller.jsonrpcCall("test_taxon_api.get_provenance", args, retType, true, true, jsonRpcContext);
        return res.get(0);
    }

    /**
     * <p>Original spec-file function name: get_id</p>
     * <pre>
     * *
     * * Retrieve object identifier.
     * * @skip documentation
     * </pre>
     * @param   ref   instance of original type "ObjectReference" (Insert your typespec information here.)
     * @return   instance of Long
     * @throws IOException if an IO exception occurs
     * @throws JsonClientException if a JSON RPC exception occurs
     */
    public Long getId(String ref, RpcContext... jsonRpcContext) throws IOException, JsonClientException {
        List<Object> args = new ArrayList<Object>();
        args.add(ref);
        TypeReference<List<Long>> retType = new TypeReference<List<Long>>() {};
        List<Long> res = caller.jsonrpcCall("test_taxon_api.get_id", args, retType, true, true, jsonRpcContext);
        return res.get(0);
    }

    /**
     * <p>Original spec-file function name: get_name</p>
     * <pre>
     * *
     * * Retrieve object name.
     * * @skip documentation
     * </pre>
     * @param   ref   instance of original type "ObjectReference" (Insert your typespec information here.)
     * @return   instance of String
     * @throws IOException if an IO exception occurs
     * @throws JsonClientException if a JSON RPC exception occurs
     */
    public String getName(String ref, RpcContext... jsonRpcContext) throws IOException, JsonClientException {
        List<Object> args = new ArrayList<Object>();
        args.add(ref);
        TypeReference<List<String>> retType = new TypeReference<List<String>>() {};
        List<String> res = caller.jsonrpcCall("test_taxon_api.get_name", args, retType, true, true, jsonRpcContext);
        return res.get(0);
    }

    /**
     * <p>Original spec-file function name: get_version</p>
     * <pre>
     * *
     * * Retrieve object version.
     * * @skip documentation
     * </pre>
     * @param   ref   instance of original type "ObjectReference" (Insert your typespec information here.)
     * @return   instance of String
     * @throws IOException if an IO exception occurs
     * @throws JsonClientException if a JSON RPC exception occurs
     */
    public String getVersion(String ref, RpcContext... jsonRpcContext) throws IOException, JsonClientException {
        List<Object> args = new ArrayList<Object>();
        args.add(ref);
        TypeReference<List<String>> retType = new TypeReference<List<String>>() {};
        List<String> res = caller.jsonrpcCall("test_taxon_api.get_version", args, retType, true, true, jsonRpcContext);
        return res.get(0);
    }
}
